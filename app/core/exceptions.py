from exceptions import CustomException


class CoreErrorCode:
    @staticmethod
    def NotFound(service_name: str, item: str):
        return CustomException(type=f"{service_name}/warning/not-found", status=404, title="Not found.", detail=f"{service_name.capitalize()} {item} could not be found.")

    @staticmethod
    def NotModified(service_name: str):
        return CustomException(type=f"{service_name}/warning/not-modified", status=304, title="Not modified.", detail="Content has not changed since the last request. No update needed.")

    @staticmethod
    def Conflict(service_name: str, item: str):
        return CustomException(type=f"{service_name}/warning/conflict", status=409, title="Conflict.", detail=f"The {item} data already exists. Please provide other data and try again.")

    @staticmethod
    def InvalidEmail(email: str):
        return CustomException(
            type="core/info/invalid-email", status=400, title="Invalid email format.", detail=f"The {email} is not a valid email. Please provide a valid email and try again."
        )

    @staticmethod
    def InvalidPhone(phone: str):
        return CustomException(
            type="core/info/invalid-phone", status=400, title="Invalid phone format.", detail=f"The {phone} is not a valid phone. Please provide a valid phone with 10 number and try again."
        )

    @staticmethod
    def InvalidDate(date: str):
        return CustomException(
            type="core/info/invalid-date", status=400, title="Invalid date format.", detail=f"The {date} is not a valid date. Please provide a valid date with YYYY-MM-DD format and try again."
        )

    @staticmethod
    def Unauthorize():
        return CustomException(type="core/warning/unauthorize", status=401, title="Unauthorize.", detail="Could not authorize credentials")
