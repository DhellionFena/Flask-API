from flask_restful import  Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST

atributos = reqparse.RequestParser()   # Pega o que o usuário passar
atributos.add_argument('login', type=str, required=True, help="The field 'login' cannot be empty")
atributos.add_argument('senha', type=str, required=True, help="The field 'senha' cannot be empty")


class User(Resource):

    # /usuarios/{user_id}
    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json()
        return {'message': 'No user found'}, 404  # Not found


    @jwt_required
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()    
                return { 'message': 'User deleted' }
            except:
                return { 'message': 'An error occurred while deleting the user'} , 500 # Internal Server Error
        
        return { 'message': 'User not found' }, 404 # not found


class UserRegister(Resource):

    # /cadastro
    def post(self):
        dados = atributos.parse_args()

        # Verifica se já existe no banco
        if UserModel.find_by_login(dados['login']):
            return {"message": f"The login {dados['login']} already exists."}
        
        user = UserModel(**dados)
        user.save_user()
        return {"message": "User created successfully!"}, 201 #Created successfully


class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = UserModel.find_by_login(dados['login'])

        if user and safe_str_cmp(user.senha, dados['senha']):
            token_de_acesso = create_access_token(identity=user.user_id)
            return {"token": token_de_acesso}, 200
        return {"message": "The username or passowrd is incorrect."}, 401 # Unauthorized


class UserLogout(Resource):

    @jwt_required
    def post(self):
        jwt_id = get_raw_jwt()['jti']  # jti == JWT Token Identifier
        BLACKLIST.add(jwt_id) # adiciona o ID a blacklist
        return {"message": "Logged out successfully"}, 200