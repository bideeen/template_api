from flask import *
from flask_mongoengine import *
from flask_jwt_extended import *
from env.api_constants import mongo_password
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)


# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)


# Database Connections
database_name = "project"
DB_URI = f"mongodb+srv://admin:{mongo_password}@cluster0.ybciz.mongodb.net/{database_name}?retryWrites=true&w=majority"
app.config["MONGODB_HOST"] = DB_URI
db = MongoEngine()
db.init_app(app)


# Defining the User schema
class User(db.Document):
    first_name = db.StringField()
    last_name = db.StringField()
    email = db.StringField()
    password = db.StringField()
    
    
    def to_json(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password
            }
        
# Defining the User schema
class Template(db.Document):
    template_name = db.StringField()
    subject = db.StringField()
    body = db.StringField()
    
    
    def to_json(self):
        return {
            "template_name": self.template_name,
            "subject": self.subject,
            "body": self.body
            }

@app.route('/')
def index():
    return "Welcome to Template API", 200


@app.route('/register', methods=['POST'])
def register():
    # get data
    content = request.get_json(force=True)
    first_name = content["first_name"]
    last_name = content["last_name"]
    email = content["email"]
    password = content["password"]
    
    # Check if email exist
    check_mail = User.objects(email=email).first()
    if check_mail:
        return make_response('Sorry, this email has been taken. Try Another Email.', 401)
    
    # save data
    user = User(
        first_name=first_name, 
        last_name=last_name, 
        email=email, 
        password=generate_password_hash(password))
    
    user.save()
    
    return make_response('Succefully Registered This User', 201)


@app.route('/login', methods=['POST'])
def login():
    """Login Details
    Details:
        email : 'lead_test@subi.com',
        password : '123456'
    Returns:
        access_token: Required access token for unique users        
    """
    try:
        content = request.get_json(force=True)
        email = content["email"]
        password = content["password"]
        
        # Check database for credentials
        user_obj = User.objects(email=email).first()
            
        print(user_obj["password"], password)
        if email == user_obj["email"] or check_password_hash(user_obj["password"], password):
            access_token = create_access_token(identity=email)
            return make_response(jsonify(access_token=access_token), 200)
        
        return make_response(jsonify({"msg": "Invalid email or password"}), 401)
    except Exception:
        return make_response(jsonify({"msg": "Invalid email or password"}), 402)

    

# Add and Fetch all templtaes
@app.route('/template', methods=['POST','GET'])
@jwt_required()
def get_all_template():
    if request.method == 'POST':
        content = request.get_json(force=True)
        temp = Template(
            template_name=content['template_name'],
            subject=content['subject'],
            body=content['body']
        )
        temp.save()
        
        return make_response('Template Added Successfully', 201)
    
    elif request.method == 'GET':
        temps = []
        for temp in Template.objects():
            temps.append(temp)            
        return make_response(jsonify(temps), 201)
    

# Fetch, Update and Delete unique templates
@app.route('/template/<template_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def fetch_template_id(temp_id):
    if request.method == 'GET':
        template_obj = Template.objects(template_name=temp_id).first()
        if template_obj:
            return make_response(jsonify(template_obj), 201)
        else:
            return make_response('No records found', 404)
    elif request.method == 'PUT':
        content = request.json
        template_obj = Template.objects(template_name=temp_id).first()
        template_obj.update(author=content['subject'], name=content['body'])
        return make_response('', 204)
    elif request.method == 'DELETE':
        template_obj = Template.objects(template_name=temp_id).first()
        template_obj.delete()
        return make_response('', 204)

# if __name__ == "__main__":
#     port = int(os.getenv("PORT", 5000))
#     app.run(host='0.0.0.0', port=port)