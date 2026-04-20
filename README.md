# Xen Orchestra Ansible Collection

An Ansible collection for managing resources in Xen Orchestra through its REST API.

## Status

This collection is published on [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/w0/xen_orchestra/).

## Requirements

- Python 3.11 or later
- `uv` for local development
- Ansible for using and building the collection

## Installation

### Ansible Galaxy

Install the collection directly from Ansible Galaxy:

```shell
ansible-galaxy collection install w0.xen_orchestra
```

### From source

1. Clone the repository:

   ```shell
   git clone https://github.com/w0/ansible-xen-orchestra.git
   ```

2. Build the collection from the repository root:

   ```shell
   ansible-galaxy collection build
   ```

3. Install the generated collection tarball:

   ```shell
   ansible-galaxy collection install ./w0-xen_orchestra-<build_version>.tar.gz
   ```

## Usage

Once installed, reference the collection by its fully qualified collection name in your playbooks.

Example:

```yaml
- hosts: localhost
  gather_facts: false
  
  module_defaults:
    group/w0.xen_orchestra.xen_orchestra:
      api_host: example.domain.com
      token: very_secure_token
      
  tasks:
    - name: Create VM Snapshot
      w0.xen_orchestra.xoa_snapshot:
        vm_uuid: "858617ef-fbda-c671-a65e-5aa3d6ad4de0"
        snapshot_name: "pre-update"
```

## Development

To set up a development environment:

1. Clone the repository.
2. Install dependencies:

   ```shell
   uv sync
   ```

3. Run your checks or tests as needed.

## Contributing

Contributions are welcome. Please open an issue or submit a pull request with any improvements, fixes, or new modules.
