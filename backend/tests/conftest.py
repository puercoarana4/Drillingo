from hypothesis import settings as hypothesis_settings

# Register Hypothesis CI profile with 100 examples per property
hypothesis_settings.register_profile("ci", max_examples=100)
hypothesis_settings.load_profile("ci")
