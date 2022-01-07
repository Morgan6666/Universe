from rest_framework.permissions import BasePermission

class IsAnonymoused(BasePermission):
    """
        Allow access only to not authenticated users
    """
    def has_permission(self, request, view):
        return bool(request.user.is_anonymous)


class IsOwnerOffTicket(BasePermission):
    """
        Allow access only user owner of ticket
    """
    message = 'Permission не обнаружен, вы не относитесь к данному тикету'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user

    def has_object_permission(self, request, view, obj):
        return bool(obj.owner == request.user)

class IsSeller(BasePermission):
    """
        Allow acces only user is seller
    """
    message = 'permission не обнаружен, вы не являетесь продавцом'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user

    def has_object_permission(self, request, view, obj):
        return bool(obj.is_seller)

class IsSellerAndHasStore(BasePermission):
    """
        Allow access only user that is seller and have store
    """
    message = 'permission  не обнаружен, вы не продавец или не имет товра'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user

    def has_object_permission(self, request, view, obj):
        has_store = True
        try:
            obj.store
        except:
            has_store = False
        return bool(obj.is_seller and has_store)

class IsSellerOfProduct(BasePermission):
    """
        Allow access only user that ssalller of product
    """
    message = 'permission не обнаружен, вы не продавец данного продукта'

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user

    def has_object_permission(self, request, view, obj):
        return bool(obj.seller.founder == request.user and request.user.is_seller)