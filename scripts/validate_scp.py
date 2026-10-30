import json
from pathlib import Path
POLICY_PATH = Path("policies/cloudtrail-protection-scp.json")
REQUIRED_ACTIONS = {
    "cloudtrail:AddTags", "cloudtrail:CreateTrail", "cloudtrail:DeleteTrail",
    "cloudtrail:RemoveTags", "cloudtrail:StartLogging", "cloudtrail:StopLogging",
    "cloudtrail:UpdateTrail",
}

def main():
    document = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if document.get("Version") != "2012-10-17":
        raise SystemExit("Unexpected policy language version")
    statements = document.get("Statement", [])
    deny_statements = [s for s in statements if s.get("Effect") == "Deny"]
    actions = {a for s in deny_statements for a in s.get("Action", [])}
    resources = {
        r for s in deny_statements
        for r in (s.get("Resource") if isinstance(s.get("Resource"), list) else [s.get("Resource")])
    }
    missing_actions = REQUIRED_ACTIONS - actions
    if missing_actions:
        raise SystemExit(f"Missing required actions: {sorted(missing_actions)}")
    if "*" not in resources:
        raise SystemExit("The deny statement must cover resource *")
    print("SCP validation passed")

if __name__ == "__main__":
    main()