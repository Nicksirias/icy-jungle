-- Trigger function to automatically create a public.users row when a new auth.users user is created
-- This solves the Foreign Key violation issue for RSVPs

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, name, location, created_at)
  VALUES (
    NEW.id,                                    -- Use the auth.users.id as the public.users.id
    NEW.email,                                 -- Copy the email from auth.users
    COALESCE(                                  -- Derive name from email or use default
      SPLIT_PART(NEW.email, '@', 1),          -- Extract username part before @
      'User'
    ),
    NULL,                                      -- Location is optional, set to NULL
    NOW()                                      -- Set created_at timestamp
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create the trigger that fires after a new user is inserted into auth.users
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- Note: This trigger will automatically run whenever a new user signs up
-- The function uses SECURITY DEFINER to ensure it has permission to insert into public.users

