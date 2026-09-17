# MIGRATION FROM CHEF INFRASTRUCTURE TO ANSIBLE

This repository contains Chef infrastructure deployment scripts and Ansible playbook examples demonstrating compliance automation with Chef InSpec. The migration scope is limited as the primary configuration management is already implemented in Ansible playbooks. The main migration effort involves replacing Chef infrastructure deployment scripts with Ansible-based infrastructure provisioning.

**Migration Complexity**: Low to Medium
**Estimated Timeline**: 2-4 weeks
**Primary Focus**: Infrastructure deployment automation and testing framework integration

## Module Migration Plan

This repository contains Chef infrastructure deployment scripts and Ansible configuration examples that need migration planning:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbooks for Apache HTTPS website deployment with SSL configuration, including security hardening (POODLE vulnerability fix) and Chef InSpec compliance testing
- Path: chef-and-ansible/
- Technology: Ansible (already migrated) with Chef InSpec testing
- Key Features: Apache 2.4.41 installation, self-signed SSL certificate generation, virtual host configuration, SSL protocol hardening, compliance verification

**setup-automate**:
- Description: Bash scripts for deploying Chef Automate and Chef Infra Server infrastructure on virtual machines
- Path: setup-automate/
- Technology: Bash scripts with Chef infrastructure deployment
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `README.md`: Repository documentation explaining Chef InSpec integration with Ansible
- `index.html`: Static test content for web server verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL security
- `tests/ssh_profile.rb`: Chef InSpec security profile for SSH root login compliance (STIG controls)

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified (on-premises or cloud-agnostic deployment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions (ansible-test, molecule, or maintain InSpec integration)
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or maintain existing Chef infrastructure for compliance reporting
- **Vagrant**: Continue using or replace with container-based testing (Docker, Podman)

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates; migration should consider proper certificate authority integration or Let's Encrypt automation
- **SSH Security Hardening**: InSpec profiles verify SSH root login restrictions; ensure Ansible playbooks maintain equivalent security controls
- **Compliance Testing**: Chef InSpec provides STIG compliance verification; migration needs equivalent Ansible-based compliance validation
- **Credential Management**: 
  - Hardcoded credentials in deployment scripts (userpassword='password')
  - Chef organization and user PEM files generated during deployment
  - SSL private keys generated on target systems
  - No vault or secrets management currently implemented

### Technical Challenges

- **Testing Framework Migration**: Replacing Chef InSpec with Ansible-native testing requires rewriting compliance tests and security profiles
- **Infrastructure Deployment**: Converting bash deployment scripts to Ansible playbooks for Chef infrastructure provisioning
- **Compliance Reporting**: Maintaining security compliance verification and reporting capabilities without Chef Automate
- **Integration Complexity**: Current setup demonstrates Chef InSpec integration with Ansible; migration may lose this hybrid capability

### Migration Order

1. **chef-and-ansible playbooks** (already Ansible-native, focus on testing framework)
2. **setup-automate scripts** (convert to Ansible infrastructure playbooks)
3. **Testing integration** (implement Molecule or maintain InSpec integration)

### Assumptions

- The organization wants to maintain compliance testing capabilities currently provided by Chef InSpec
- Existing Ansible playbooks in chef-and-ansible/ directory are considered the target state for configuration management
- Chef infrastructure (Automate/Infra Server) deployment needs to be maintained or replaced with equivalent Ansible infrastructure
- Test Kitchen and Vagrant testing workflow should be replaced with Ansible-native alternatives
- Security compliance requirements (STIG controls) must be maintained in the migrated solution
- The hybrid Chef InSpec + Ansible approach may be intentional and could be preserved rather than fully migrated