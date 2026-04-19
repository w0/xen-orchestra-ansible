# Xen Orchestra Ansible Collection

An Ansible collection for managing resources in Xen Orchestra through its REST API.

## Status

This project is under active development. The collection is not yet published to Ansible Galaxy.

## Requirements

- Python 3.11 or later
- `uv` for local development
- Ansible for using and building the collection

## Development

To set up a development environment:

1. Clone the repository.
2. Install dependencies:

   ```shell
   uv sync
   ```

3. Run your checks or tests as needed.

## Installation

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

### Ansible Galaxy

This collection is not yet available on Ansible Galaxy.

## Usage

Once installed, reference the collection by its fully qualified collection name in your playbooks.

Example:

```yaml
- hosts: localhost
  gather_facts: false
  tasks:
    - name: Use a Xen Orchestra module
      w0.xen_orchestra.your_module_here:
        # module options here
```

## Contributing

Contributions are welcome. Please open an issue or submit a pull request with any improvements, fixes, or new modules.