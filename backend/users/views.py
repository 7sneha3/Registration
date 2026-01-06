from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.mail import send_mail
from pymongo import MongoClient
from datetime import datetime
import hashlib
import re


# MongoDB connection
def get_db():
    try:
        # Add connection options for better reliability
        # mongodb+srv:// automatically handles SSL/TLS
        client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=30000,  # Increased timeout
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
        )
        # Test the connection
        client.admin.command('ping')
        db = client[settings.MONGODB_DB_NAME]
        return db
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        # Mask password in error message
        uri_display = settings.MONGODB_URI
        if '@' in uri_display:
            parts = uri_display.split('@')
            user_pass = parts[0]
            if '://' in user_pass:
                user_pass_parts = user_pass.split('://')
                if ':' in user_pass_parts[-1]:
                    username = user_pass_parts[-1].split(':')[0]
                    uri_display = f"{user_pass_parts[0]}://{username}:***@{parts[1]}"
        print(f"Connection URI: {uri_display}")
        raise


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password (at least 8 characters)"""
    return len(password) >= 8

@api_view(['POST'])
@permission_classes([AllowAny])
@method_decorator(csrf_exempt, name='dispatch')
def signup(request):
    """
    User registration endpoint
    Expected JSON payload:
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securepassword123",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    try:
        data = request.data
        
        # Extract fields
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        # Validation
        if not username:
            return Response(
                {'error': 'Username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not validate_email(email):
            return Response(
                {'error': 'Invalid email format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not validate_password(password):
            return Response(
                {'error': 'Password must be at least 8 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Connect to MongoDB
        try:
            db = get_db()
            users_collection = db.signup
        except Exception as e:
            return Response(
                {'error': f'MongoDB connection failed: {str(e)}. Please check your MONGODB_URI and credentials.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Check if user already exists
        if users_collection.find_one({'$or': [{'email': email}, {'username': username}]}):
            return Response(
                {'error': 'User with this email or username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Hash password (simple hash - in production, use bcrypt or similar)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user document
        user_data = {
            'username': username,
            'email': email,
            'password': password_hash,
            'first_name': first_name,
            'last_name': last_name,
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        # Insert user into database
        result = users_collection.insert_one(user_data)
        
        # Send registration confirmation email
        try:
            subject = 'Welcome! Registration Successful'
            message = f"""
Hello {first_name or username},

Thank you for registering with us!

Your account has been successfully created with the following details:
- Username: {username}
- Email: {email}

We're excited to have you on board!

Best regards,
The Team
            """
            # commented at 4:19pm
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            # Log email error but don't fail registration
            print(f"Error sending email: {str(e)}")
        
        return Response(
            {
                'message': 'User registered successfully! Please check your email for confirmation.',
                'user_id': str(result.inserted_id)
            },
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

