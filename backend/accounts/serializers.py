from django.contrib.auth import get_user_model, password_validation
from django.db.models import Q
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, required=False, min_length=8, max_length=72)

  class Meta:
    model = User
    fields = (
        "id",
        "username",
        "email",
        "password",
        "full_name",
        "profile_photo",
        "role",
        "is_active",
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
    )
    read_only_fields = ("id", "last_login", "date_joined", "created_at", "updated_at")

  def validate_email(self, value: str) -> str:
    email = value.strip().lower()
    queryset = User.objects.filter(email__iexact=email)
    if self.instance:
      queryset = queryset.exclude(pk=self.instance.pk)
    if queryset.exists():
      raise serializers.ValidationError("Email is already registered.")
    return email

  def validate_username(self, value: str) -> str:
    username = value.strip()
    queryset = User.objects.filter(username__iexact=username)
    if self.instance:
      queryset = queryset.exclude(pk=self.instance.pk)
    if queryset.exists():
      raise serializers.ValidationError("Username is already registered.")
    return username

  def validate_password(self, value: str) -> str:
    password_validation.validate_password(value, self.instance)
    return value

  def create(self, validated_data):
    password = validated_data.pop("password", None)
    user = User(**validated_data)
    if password:
      user.set_password(password)
    else:
      user.set_unusable_password()
    user.save()
    return user

  def update(self, instance, validated_data):
    password = validated_data.pop("password", None)
    user = super().update(instance, validated_data)
    if password:
      user.set_password(password)
      user.save(update_fields=["password", "updated_at"])
    return user


class RegisterSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, min_length=8, max_length=72)

  class Meta:
    model = User
    fields = ("username", "email", "password", "full_name")

  def validate_email(self, value: str) -> str:
    email = value.strip().lower()
    if User.objects.filter(email__iexact=email).exists():
      raise serializers.ValidationError("Email is already registered.")
    return email

  def validate_username(self, value: str) -> str:
    username = value.strip()
    if User.objects.filter(username__iexact=username).exists():
      raise serializers.ValidationError("Username is already registered.")
    return username

  def validate_password(self, value: str) -> str:
    password_validation.validate_password(value)
    return value

  def create(self, validated_data):
    password = validated_data.pop("password")
    user = User(**validated_data)
    user.set_password(password)
    user.save()
    return user


class LoginSerializer(serializers.Serializer):
  identifier = serializers.CharField(required=False)
  email = serializers.EmailField(required=False)
  password = serializers.CharField(write_only=True)

  def validate(self, attrs):
    identifier = attrs.get("identifier") or attrs.get("email")
    if not identifier:
      raise serializers.ValidationError({"identifier": "This field is required."})

    attrs["identifier"] = identifier.strip()
    return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ("username", "email", "full_name", "profile_photo")

  def validate_email(self, value: str) -> str:
    email = value.strip().lower()
    existing_user = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).first()
    if existing_user:
      raise serializers.ValidationError("Email is already registered.")
    return email

  def validate_username(self, value: str) -> str:
    username = value.strip()
    existing_user = User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).first()
    if existing_user:
      raise serializers.ValidationError("Username is already registered.")
    return username


class PasswordChangeSerializer(serializers.Serializer):
  current_password = serializers.CharField(write_only=True)
  new_password = serializers.CharField(write_only=True, min_length=8, max_length=72)

  def validate_current_password(self, value: str) -> str:
    user = self.context["request"].user
    if not user.check_password(value):
      raise serializers.ValidationError("Current password is incorrect.")
    return value

  def validate_new_password(self, value: str) -> str:
    password_validation.validate_password(value, self.context["request"].user)
    return value


def find_user_by_identifier(identifier: str):
  return User.objects.filter(
      Q(email__iexact=identifier.strip()) | Q(username__iexact=identifier.strip())
  ).first()
