from supabase_client import supabase

def sign_up(email, password, full_name):
    """Register new user"""
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        user = response.user

        if user:
            # Try to save name to profiles table (optional)
            try:
                supabase.table("profiles").insert({
                    "id": user.id,
                    "full_name": full_name
                }).execute()
            except Exception as profile_err:
                # Profile table may not exist yet, but signup is still successful
                print(f"Warning: Could not save profile: {profile_err}")

        return True, "Account created successfully! Please login with your credentials."
    except Exception as e:
        error_str = str(e).lower()
        if "already exists" in error_str or "user already registered" in error_str:
            return False, "Email already registered. Please login instead."
        elif "password" in error_str:
            return False, "Password does not meet requirements (min 6 characters)."
        else:
            return False, f"Signup failed: {str(e)}"


def sign_in(email, password):
    """Login existing user"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            return True, response.user
        else:
            return False, "Invalid email or password."
    except Exception as e:
        error_str = str(e).lower()
        if "invalid credentials" in error_str or "invalid login" in error_str:
            return False, "Invalid email or password."
        elif "user not found" in error_str:
            return False, "No account found with this email. Please sign up."
        else:
            return False, f"Login failed: {str(e)}"


def sign_out():
    """Logout user"""
    supabase.auth.sign_out()


def get_profile(user_id):
    """Get user profile from database"""
    try:
        response = supabase.table("profiles")\
            .select("*")\
            .eq("id", user_id)\
            .execute()
        if response.data:
            return response.data[0]
        return None
    except:
        return None


def save_profile(user_id, profile_data):
    """Save or update user profile"""
    try:
        existing = get_profile(user_id)
        if existing:
            # Update existing profile
            supabase.table("profiles")\
                .update(profile_data)\
                .eq("id", user_id)\
                .execute()
        else:
            # Create new profile
            profile_data["id"] = user_id
            supabase.table("profiles")\
                .insert(profile_data)\
                .execute()
        return True, "Profile saved!"
    except Exception as e:
        return False, str(e)


def save_meal_plan(user_id, plan_text,
                   daily_calories, goal,
                   diet_type, feedback=""):
    """Save meal plan to database"""
    try:
        supabase.table("meal_plans").insert({
            "user_id": user_id,
            "plan_text": plan_text,
            "daily_calories": daily_calories,
            "goal": goal,
            "diet_type": diet_type,
            "feedback": feedback
        }).execute()
        return True, "Plan saved!"
    except Exception as e:
        return False, str(e)


def get_saved_plans(user_id):
    """Get all saved plans for a user"""
    try:
        response = supabase.table("meal_plans")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        return response.data
    except:
        return []


def delete_meal_plan(plan_id):
    """Delete a saved meal plan"""
    try:
        supabase.table("meal_plans")\
            .delete()\
            .eq("id", plan_id)\
            .execute()
        return True
    except:
        return False