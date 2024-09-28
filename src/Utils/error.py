class Error:
    def __init__(self, error_code: int):
        match error_code:
            case 1:
                message = "Username already exists"
            case 2:
                message = "Username or password is incorrect"
            case 3:
                message = "Subject already exists"
            case 4:
                message = "Subject does not exist"
            case 5:
                message = "User is not logged in"
            case 6:
                message = "Reply does not exist"
            case 7:
                message = "Reply does not belong to user"
            case 8:
                message = "User is not authorized to delete"
            case 9:
                message = "User is not authorized to delete reply"
            case 10:
                message = "User Not Registered"
            case 11:
                message = "Subject has more than 0 replies, cannot delete"
            case 12:
                message = "User has not replied to this subject"
            case 13:
                message = "User is not authorized to view, only Admin can view"
            case _:
                message = f'{error_code}'
        self.message = message

    def __str__(self):
        return self.message
