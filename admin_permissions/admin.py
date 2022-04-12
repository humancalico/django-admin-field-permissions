# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import enum


class PermissionType(enum.Enum):
    VIEW = 1,
    CHANGE = 2,


def get_permission_type(perm_string):
    # FIXME also raise the same exception if unable to split or index
    # perm_string would be of the format can_change_somefield or can_view_somefield
    if perm_string.split("_")[1] == "change":
        return PermissionType.CHANGE
    elif perm_string.split("_")[1] == "view":
        return PermissionType.VIEW
    else:
        raise Exception(
            "Illegal format to create permission. Please create them in the following format: can_change_* or can_view_*")


def get_other_permission_type(perm_string):
    if get_permission_type(perm_string) == PermissionType.VIEW:
        return f'can_change_{perm_string.removeprefix("can_view_")}'
    elif get_permission_type(perm_string) == PermissionType.CHANGE:
        return f'can_view_{perm_string.removeprefix("can_change_")}'


class FieldPermissionMixin(object):
    """Adds simple functionality to check the permissions for the fields"""
    fields_permissions = {}

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(FieldPermissionMixin, self).get_fieldsets(request, obj).copy()

        for permission, fields in self.fields_permissions.items():
            if (not request.user.has_perm(permission)) or (
                    not request.user.has_perm(get_other_permission_type(permission))):
                if isinstance(fields, (str, list)):
                    fields = (fields,)
                fieldsets = self.remove_fields(fieldsets, *fields)

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        fieldsets = super(FieldPermissionMixin, self).get_readonly_fields(request, obj).copy()

        # if user has view perm but not corresponding change perm
        read_only_perms = filter(lambda elem: get_permission_type(elem[0]) == PermissionType.VIEW,
                                 self.fields_permissions)
        for permission, fields in read_only_perms.items():
            if request.user.has_perm(permission) and (not request.user.has_perm(get_other_permission_type(permission))):
                if isinstance(fields, (str, list)):
                    fields = (fields,)
                fieldsets += fields

        return fieldsets

    @staticmethod
    def remove_fields(fieldsets, *remove_fields):
        """
        Removes all the anterior field,
        if there is no fieldsets available fields, it is also removed,
        Returns the modified fieldsets
        """
        for count, fs in enumerate(fieldsets):
            fs[1]['fields'] = [field for field in fs[1]['fields'] if field not in remove_fields]
            if not fs[1]['fields']:
                fieldsets.pop(count)
        return fieldsets
