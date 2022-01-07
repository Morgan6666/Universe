from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone, name, password = None):
        if not phone:
            raise ValueError('Пропущена графа с номером телефона')
        if not name:
            raise ValueError('Пропущена графа с именем')

        user = self.model(
            phone = phone,
            name = name,
        )

        user.set_password(password)
        user.save(using = self._db)
        return user

