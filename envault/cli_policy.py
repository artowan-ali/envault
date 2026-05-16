"""CLI commands for managing vault key policies."""

from envault.policy import set_policy, remove_policy, get_policy, list_policies, validate
from envault.vault import Vault


def cmd_policy_set(args, password: str) -> None:
    """Set a policy rule for a key."""
    set_policy(args.vault_dir, args.key, required=args.required, pattern=args.pattern)
    parts = []
    if args.required:
        parts.append("required=true")
    if args.pattern:
        parts.append(f"pattern={args.pattern}")
    desc = ", ".join(parts) if parts else "(no constraints)"
    print(f"Policy set for '{args.key}': {desc}")


def cmd_policy_remove(args, password: str) -> None:
    """Remove a policy rule."""
    removed = remove_policy(args.vault_dir, args.key)
    if removed:
        print(f"Policy removed for '{args.key}'.")
    else:
        print(f"No policy found for '{args.key}'.")


def cmd_policy_show(args, password: str) -> None:
    """Show the policy for a specific key."""
    policy = get_policy(args.vault_dir, args.key)
    if policy is None:
        print(f"No policy set for '{args.key}'.")
    else:
        print(f"Key:      {args.key}")
        print(f"Required: {policy.get('required', False)}")
        print(f"Pattern:  {policy.get('pattern') or '(none)'}")


def cmd_policy_list(args, password: str) -> None:
    """List all policies."""
    policies = list_policies(args.vault_dir)
    if not policies:
        print("No policies defined.")
        return
    for key, rule in sorted(policies.items()):
        req = "required" if rule.get("required") else "optional"
        pat = rule.get("pattern") or "*"
        print(f"  {key}: {req}, pattern={pat}")


def cmd_policy_validate(args, password: str) -> None:
    """Validate current vault contents against all policies."""
    vault = Vault(args.vault_dir, password)
    store = {k: vault.get(k) for k in vault.list_keys()}
    violations = validate(args.vault_dir, store)
    if not violations:
        print("All policies satisfied.")
    else:
        print(f"{len(violations)} violation(s) found:")
        for v in violations:
            print(f"  [{v['key']}] {v['reason']}")


def register_policy_commands(subparsers) -> None:
    p = subparsers.add_parser("policy-set", help="Set a policy for a key")
    p.add_argument("key")
    p.add_argument("--required", action="store_true", default=False)
    p.add_argument("--pattern", default=None)
    p.set_defaults(func=cmd_policy_set)

    p = subparsers.add_parser("policy-remove", help="Remove a policy")
    p.add_argument("key")
    p.set_defaults(func=cmd_policy_remove)

    p = subparsers.add_parser("policy-show", help="Show policy for a key")
    p.add_argument("key")
    p.set_defaults(func=cmd_policy_show)

    p = subparsers.add_parser("policy-list", help="List all policies")
    p.set_defaults(func=cmd_policy_list)

    p = subparsers.add_parser("policy-validate", help="Validate vault against policies")
    p.set_defaults(func=cmd_policy_validate)
