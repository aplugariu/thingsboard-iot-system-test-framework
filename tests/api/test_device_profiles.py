def test_energy_meter_profile_exists(device_profiles):
    profile = device_profiles.get_by_name("Energy Meter")

    assert profile.name == "Energy Meter"
    assert profile.id