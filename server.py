from flask import Flask
from flask_restful import Api, Resource, reqparse
from datetime import datetime

app = Flask(__name__)
api = Api(app)


class Message(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("created_at")
        parser.add_argument("id")
        parser.add_argument("sender_id")
        parser.add_argument("text")
        parser.add_argument("name")
        args = parser.parse_args()

        created_at = int(args["created_at"])
        message = {
            "created_at": datetime.utcfromtimestamp(created_at).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "message_id": args["id"],
            "sender_id": args["sender_id"],
            "name": args["name"],
            "text": args["text"]
        }
        request = args["text"].split()
        if request[1] == 'search':
            print('searching')

        #insert message into table

        return message, 201


api.add_resource(Message, "/Adolf")
app.run(debug=True)