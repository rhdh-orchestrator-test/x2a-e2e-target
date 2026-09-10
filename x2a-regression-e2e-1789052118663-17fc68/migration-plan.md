# MIGRATION FROM CHEF ECOSYSTEM TO ANSIBLE

This repository contains Chef-related examples and deployment scripts rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, Chef server deployment scripts, and compliance testing examples. The migration scope is minimal as the repository already contains Ansible content and supporting infrastructure.

## Module Migration Plan

This repository contains demonstration and deployment content rather than production Chef cookbooks:

### MODULE INVENTORY

**No Chef cookbooks found for migration.** The repository contains:

- **chef-and-ansible examples**: 
    - Description: Ansible playbooks demonstrating Apache HTTPS configuration with Chef InSpec compliance testing
    - Path: chef-and-ansible/
    - Technology: Ansible (already migrated) + Chef InSpec
    - Key Features: SSL certificate generation, Apache virtual host configuration, POODLE vulnerability remediation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for Apache HTTPS setup with self-signed certificates
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disables SSLv3, enables TLSv1.2)
- `chef-and-ansible/index.html`: Static HTML test content
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with deployment scripts targeting Linux systems
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - deployment scripts support both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Continue using for compliance testing alongside Ansible - no migration required
- **Test Kitchen**: Already configured for Ansible playbook testing - no changes needed
- **Apache 2.4.41**: Specific version pinned in playbook - verify availability in target environment
- **OpenSSL/PyOpenSSL**: Required for certificate generation - standard Ansible dependencies

### Security Considerations

- **SSL/TLS Configuration**: Playbooks implement proper SSL hardening (disables SSLv3, enforces TLSv1.2)
- **Self-signed Certificates**: Current implementation uses self-signed certs for testing - consider CA-signed certificates for production
- **SSH Hardening**: InSpec tests verify SSH root login is disabled (compliance control SRG-OS-000112)
- **Credential Management**: Deployment scripts contain hardcoded credentials (username: 'jtonello', password: 'password') - must be externalized using Ansible Vault or environment variables
- **File Permissions**: Proper file permissions implemented (0640 for certs, 0755 for directories)

### Technical Challenges

- **Minimal Migration Required**: Repository already contains Ansible content - primary challenge is credential management in deployment scripts
- **InSpec Integration**: Existing Chef InSpec tests can continue to be used with Ansible for compliance validation
- **Deployment Script Modernization**: Bash deployment scripts should be converted to Ansible playbooks for consistency and idempotency

### Migration Order

1. **Credential Externalization** (immediate priority): Remove hardcoded credentials from deployment scripts
2. **Deployment Script Conversion** (low complexity): Convert bash scripts to Ansible playbooks for Chef server deployment
3. **Testing Framework Validation** (verification): Ensure existing Test Kitchen + InSpec integration continues to function

### Assumptions

- The repository serves as a demonstration/example collection rather than production infrastructure code
- Existing Ansible playbooks are considered the target state rather than source material for migration
- Chef InSpec will continue to be used for compliance testing alongside Ansible
- The Test Kitchen configuration is intended for development/testing environments only
- Deployment scripts are used for lab/demo environments based on the hardcoded credentials and domain names
- No production Chef cookbooks exist in this repository that require migration to Ansible roles
- The Apache configuration in the playbooks represents the desired end state for web server setup