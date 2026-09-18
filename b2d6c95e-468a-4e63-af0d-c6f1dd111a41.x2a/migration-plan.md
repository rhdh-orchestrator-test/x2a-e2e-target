# MIGRATION FROM CHEF TO ANSIBLE

**EXECUTIVE SUMMARY**: This repository does not contain traditional Chef cookbooks requiring migration to Ansible. Instead, it contains demonstration materials showing how Chef InSpec can be integrated with Ansible for compliance automation. The repository includes Ansible playbooks, InSpec compliance tests, and Chef server deployment scripts. No cookbook-to-playbook migration is required, but the InSpec integration patterns and deployment scripts may need modernization.

**SCOPE**: 2 Ansible playbooks, 2 InSpec test suites, 2 Chef server deployment scripts
**COMPLEXITY**: Low - primarily documentation and example updates
**TIMELINE ESTIMATE**: 1-2 weeks for modernization and documentation updates

## Module Migration Plan

This repository contains demonstration materials and deployment scripts rather than production Chef cookbooks:

### MODULE INVENTORY

**No Chef cookbooks found for migration.** The repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates and SSL hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4 installation, SSL certificate generation, virtual host configuration, security hardening

- **poodle_fix**:
    - Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration updates, POODLE vulnerability mitigation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen)
- **Cloud Platform**: Not specified (local development focus)

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies found.** Current dependencies include:
- **Apache 2.4.41**: Already configured in Ansible playbook
- **OpenSSL/PyOpenSSL**: Certificate management handled by Ansible modules
- **Test Kitchen**: Integration testing framework for Ansible + InSpec

### Security Considerations

- **SSL/TLS Configuration**: Playbooks demonstrate proper SSL hardening practices
  - Self-signed certificate generation using Ansible openssl modules
  - SSL protocol restrictions (TLS 1.2 only, SSLv3 disabled)
  - Proper file permissions on certificate files (0640)
- **SSH Hardening**: InSpec profile validates SSH root login restrictions
- **No hardcoded credentials**: All sensitive data uses variables or generated certificates
- **STIG Compliance**: SSH profile includes STIG control mappings and severity ratings

### Technical Challenges

- **Documentation Updates**: Repository documentation needs clarification that this is a demonstration of Ansible + InSpec integration, not a Chef-to-Ansible migration example
- **Test Kitchen Configuration**: Current setup uses older Ansible provisioner syntax that may need updates for newer Test Kitchen versions
- **Chef Server Dependencies**: Deployment scripts install Chef Automate/Server but may not be needed if focus shifts to pure Ansible + InSpec workflows

### Migration Order

**No migration required** - content is already Ansible-based. Recommended modernization order:

1. **Documentation Updates** (immediate) - Clarify repository purpose and update examples
2. **Test Kitchen Modernization** (low priority) - Update provisioner configuration for current versions
3. **Chef Server Script Review** (optional) - Evaluate if deployment scripts are still needed for demonstration purposes

### Assumptions

- Repository serves as educational/demonstration material rather than production infrastructure code
- InSpec integration with Ansible is the primary value proposition, not Chef cookbook migration
- Test Kitchen + Vagrant setup is intended for local development and testing
- Chef server deployment scripts are for setting up test environments, not production deployments
- Ubuntu 20.04 target may need updating to more current LTS versions for production use
- Self-signed certificates are acceptable for demonstration purposes but would need proper CA certificates for production
- SSH hardening requirements follow RHEL 8 STIG guidelines but are applied to Ubuntu systems