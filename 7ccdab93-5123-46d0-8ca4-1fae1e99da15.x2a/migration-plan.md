# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests and Ansible playbooks demonstrating hybrid automation approaches. The migration scope is limited as this is primarily a demonstration repository rather than production infrastructure code. The main migration effort involves consolidating InSpec compliance testing into native Ansible testing approaches and removing Chef infrastructure dependencies.

**Timeline Estimate**: 1-2 weeks (low complexity due to minimal Chef components)

## Module Migration Plan

This repository contains Chef InSpec compliance tests and supporting infrastructure that need migration planning:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS website deployment with SSL/TLS configuration and compliance verification using Chef InSpec
- Path: chef-and-ansible/
- Technology: Ansible playbooks with Chef InSpec testing
- Key Features: Self-signed SSL certificate generation, Apache virtual host configuration, POODLE vulnerability mitigation, compliance testing for HTTPS and SSH security controls

**chef-infrastructure-setup**:
- Description: Chef Automate and Chef Infra Server deployment scripts for demonstration environment
- Path: setup-automate/
- Technology: Bash scripts with Chef Automate CLI
- Key Features: Automated Chef server deployment, user and organization creation, system tuning for Chef Automate

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration using Ansible provisioner with InSpec verifier - needs migration to molecule or native Ansible testing
- `website_https.yml`: Ansible playbook for Apache HTTPS setup - already in target format, minimal changes needed
- `poodle_fix.yml`: Ansible playbook for SSL security hardening - already in target format
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality - needs conversion to Ansible testing modules
- `tests/ssh_profile.rb`: InSpec SSH security compliance profile - needs conversion to Ansible security testing
- `deploy-automate.sh`: Chef Automate deployment script - needs replacement with Ansible-based infrastructure provisioning
- `deploy-chef-server.sh`: Chef Infra Server deployment script - needs replacement with Ansible-based infrastructure provisioning

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with ansible-lint, molecule testing framework, and native Ansible testing modules (uri, assert, etc.)
- **Test Kitchen**: Replace with Molecule for infrastructure testing and validation
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or native CI/CD pipeline integration
- **Vagrant**: Can be retained as virtualization platform or migrated to container-based testing

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks already implement proper SSL certificate management using Ansible's openssl modules - minimal migration needed
- **SSH Hardening**: InSpec SSH compliance tests need conversion to Ansible's built-in security modules and assert tasks
- **Compliance Testing**: 
  - Current InSpec tests verify HTTPS functionality, SSL protocol compliance, and SSH security controls
  - Migration requires implementing equivalent checks using Ansible's uri module, assert module, and lineinfile verification
  - STIG compliance controls (SRG-OS-000112, V-38607) currently tested via InSpec need native Ansible validation

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec compliance tests to native Ansible testing requires restructuring test logic from Ruby-based InSpec controls to YAML-based Ansible tasks
- **Compliance Reporting**: InSpec provides detailed compliance reporting that needs equivalent implementation in Ansible testing framework
- **Infrastructure Provisioning**: Chef Automate deployment scripts need complete rewrite using Ansible infrastructure modules or integration with existing Ansible automation platform

### Migration Order

1. **website-https-compliance** (Priority 1): Convert InSpec tests to Ansible native testing, update existing playbooks for any compatibility issues
2. **chef-infrastructure-setup** (Priority 2): Replace Chef deployment scripts with Ansible-based infrastructure provisioning or remove if demonstration-only

### Assumptions

- This repository serves as a demonstration/example rather than production infrastructure, reducing migration complexity
- The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already in target format and require minimal changes
- Test Kitchen and InSpec dependencies can be replaced with Molecule and native Ansible testing without loss of functionality
- Chef Automate/Infra Server deployment scripts may be removed entirely if they serve only demonstration purposes
- The target environment will use Ansible AWX/Tower or similar for centralized automation management instead of Chef Automate
- Compliance requirements currently met by InSpec can be satisfied using Ansible's built-in security and testing modules
- The Ubuntu 20.04 target platform and Vagrant virtualization can be retained in the migrated solution