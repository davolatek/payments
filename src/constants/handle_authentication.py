from src.models import User
from werkzeug.security import check_password_hash
class authentication:
    def handle_auth(request):
        is_authenticated= False
        message = ""
        email = request.headers.get('email')
        password = request.headers.get('password')
        if email and password:
            user = User.query.filter_by(email=email).first()

            if user is None:
                is_authenticated = False
                message = "No user found"
            else:
                if check_password_hash(user.password, password):
                    is_authenticated = True
                    message = "validated"
        else:
            is_authenticated = False
            message = "No credentials provided"

        return {"is_authenticated":is_authenticated, "message": message}