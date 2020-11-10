from flask_restful import  Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required

class Hoteis(Resource):
    def get(self):
        return {'hoteis': [hotel.json() for hotel in HotelModel.query.all()]}

class Hotel(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help="The field 'name' cannot be empty.")
    argumentos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas' cannot be left blank.")
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'message': 'No hotel found'}, 404  # Not found

    @jwt_required  # Precisa do token de acesso
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {'message': f'Hotel id {hotel_id} already exists'},  400  # Bad request
        
        dados = Hotel.argumentos.parse_args()
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return { 'message': 'An error occurred while saving the hotel' }, 500 # Internal Server Error
        return hotel.json(), 200   # Success!

    @jwt_required
    def put(self, hotel_id):
        # Filtro
        dados = Hotel.argumentos.parse_args()
        hotel_encontrado = HotelModel.find_hotel(hotel_id)

        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200

        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return { 'message': 'An error occurred while saving the hotel' }, 500 # Internal Server Error
        return hotel.json(), 201     # created

    @jwt_required
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()    
                return { 'message': 'Hotel deleted' }
            except:
                return { 'message': 'An error occurred while deleting the hotel'} , 500 # Internal Server Error
        
        return { 'message': 'Hotel not found' }, 404 # not found
