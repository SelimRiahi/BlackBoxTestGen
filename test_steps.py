from behave import given, when, then

@given('there is no authenticated user')
def step_impl(context):
    pass


@when('the user navigates to registration page')
def step_impl(context):
    pass


@when('provides a valid username and password')
def step_impl(context):
    pass


@then('the system should return a success message')
def step_impl(context):
    pass


@then("""store the user's credentials securely""")
def step_impl(context):
    pass


@then('generate a JWT token')
def step_impl(context):
    pass


