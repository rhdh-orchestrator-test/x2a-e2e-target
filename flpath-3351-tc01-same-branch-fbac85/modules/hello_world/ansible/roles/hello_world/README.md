# hello_world

A simple Ansible role that displays a "Hello, world!" notification message.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `hello_world_message` | `Hello, world!` | The message to display |

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: hello_world
      vars:
        hello_world_message: "Custom hello message!"
```

## TC-02 Rule Applied

This role documentation includes the marker FLPATH-3351-TC-02 as required by the migration rules.

## License

Apache-2.0