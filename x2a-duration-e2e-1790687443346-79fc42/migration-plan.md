# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible playbooks, rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks with InSpec test verification and Chef server deployment scripts. Migration complexity is **LOW** as the core infrastructure automation is already implemented in Ansible - the main task is replacing InSpec testing with native Ansible testing approaches.

**Timeline Estimate**: 1-2 weeks for a small team to refactor testing approach and deployment scripts.

## Module Migration Plan

This repository contains demonstration code and deployment utilities that need assessment for production use:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths verified from the provided repository tree structure.

- **website-https-demo**:
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL protocol enforcement (TLS 1.2)

- **poodle-ssl-fix**:
    - Description: Ansible playbook for SSL/TLS security hardening, specifically disabling vulnerable SSL protocols and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration hardening, protocol version enforcement, POODLE vulnerability mitigation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification - needs migration to molecule or native Ansible testing
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality - requires conversion to Ansible testing modules
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance tests for SSH configuration - needs conversion to Ansible assert tasks
- `chef-and-ansible/index.html`: Static test content for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script - requires replacement with Ansible automation
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - requires replacement with Ansible automation

### Target Details

Based on the Ansible playbooks and deployment scripts:

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with RHEL compatibility indicated in InSpec tests
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing), production deployment appears cloud-agnostic
- **Cloud Platform**: Not specified - deployment scripts are generic and work across cloud providers

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible's built-in testing modules (assert, uri, service, etc.) and ansible-test framework
- **Test Kitchen**: Migrate to Molecule for Ansible playbook testing and verification
- **Chef Automate/Server**: Replace deployment automation with Ansible playbooks for infrastructure provisioning

### Security Considerations

- **SSL/TLS Configuration Management**: Current playbooks demonstrate proper SSL hardening practices that should be maintained
  - Self-signed certificate generation using OpenSSL Ansible modules
  - TLS protocol enforcement (disabling SSL 3.0, enforcing TLS 1.2+)
  - Apache SSL configuration best practices
- **SSH Security Compliance**: InSpec tests verify SSH root login restrictions - convert to Ansible assert tasks
- **Certificate Management**: Current implementation uses self-signed certificates - consider integration with Let's Encrypt or enterprise CA
- **Secrets Management**: Deployment scripts contain hardcoded credentials that need to be externalized to Ansible Vault

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec compliance tests to native Ansible testing requires rewriting test logic using Ansible modules (assert, uri, command, etc.)
- **Chef Server Replacement**: Deployment scripts for Chef infrastructure need complete replacement with Ansible-based infrastructure provisioning
- **Compliance Verification**: InSpec provides detailed compliance reporting - need to implement equivalent reporting with Ansible testing modules

### Migration Order

1. **Testing Framework Conversion** (Priority 1 - foundational)
   - Convert InSpec tests to Ansible assert tasks and testing modules
   - Replace Test Kitchen with Molecule for playbook testing
   
2. **Infrastructure Deployment Automation** (Priority 2 - operational)
   - Replace Chef server deployment scripts with Ansible playbooks
   - Implement proper secrets management with Ansible Vault
   
3. **Enhanced Security Automation** (Priority 3 - improvement)
   - Integrate Let's Encrypt for certificate management
   - Implement comprehensive compliance reporting

### Assumptions

- The current Ansible playbooks are demonstration code and may need hardening for production use
- InSpec test coverage represents the minimum compliance requirements that must be maintained post-migration
- The Chef server deployment scripts are used for setting up test/development environments rather than production infrastructure
- SSL certificate management will need to be enhanced beyond self-signed certificates for production use
- The target environment supports the same package versions and configurations demonstrated in the examples
- Team has experience with Ansible testing frameworks or can acquire necessary training
- Current hardcoded credentials in deployment scripts are acceptable for development but must be secured for production use