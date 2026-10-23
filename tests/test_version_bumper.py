from scripts.bump_version import bump_semver, get_current_version

def test_bump_semver_rules():
    assert bump_semver("1.0.0", "patch") == "1.0.1"
    assert bump_semver("1.0.9", "patch") == "1.0.10"
    assert bump_semver("1.0.5", "minor") == "1.1.0"
    assert bump_semver("1.9.3", "minor") == "1.10.0"
    assert bump_semver("1.5.2", "major") == "2.0.0"
    assert bump_semver("v1.1.0", "patch") == "1.1.1"

    curr = get_current_version()
    assert curr == "1.4.2", f"Expected current version 1.4.2, got {curr}"
    print("test_version_bumper passed successfully!")

if __name__ == "__main__":
    test_bump_semver_rules()
