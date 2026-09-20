# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository is a demonstration/examples repository that showcases Chef InSpec integration with Ansible playbooks rather than a traditional Chef cookbook repository requiring migration. The content is already primarily Ansible-based with Chef InSpec used for compliance testing. The migration scope is minimal as the core infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains example configurations and deployment scripts that demonstrate Chef InSpec integration with Ansible:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbook examples demonstrating Apache HTTPS website deployment with SSL configuration and POODLE vulnerability remediation, integrated with Chef InSpec compliance testing
- Path: chef-and-ansible/
- Technology: Ansible (with Chef InSpec for testing)
- Key Features: Apache 2.4 installation, SSL certificate generation, virtual host configuration, security hardening, Test Kitchen integration

**setup-automate**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server installation on virtual machines
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `website_https.yml`: Ansible playbook for Apache HTTPS site deployment with SSL certificates
- `poodle_fix.yml`: Ansible playbook for SSL security hardening (POODLE vulnerability mitigation)
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `tests/ssh_profile.rb`: Chef InSpec security profile for SSH root login compliance (STIG controls)
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation script
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with Chef server deployment targeting Linux systems
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen for local testing)
- **Cloud Platform**: Not specified, designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated for compliance testing - no migration needed, continue using InSpec with Ansible
- **Test Kitchen**: Currently configured for Ansible playbook testing - maintain existing integration
- **Apache 2.4.41**: Specific version pinned in playbook - verify availability in target environment
- **OpenSSL/PyOpenSSL**: Required for SSL certificate generation - standard Ansible crypto modules already in use

### Security Considerations

- **SSL/TLS Configuration**: Playbooks already implement proper SSL certificate generation and POODLE vulnerability mitigation
- **SSH Hardening**: InSpec profiles verify SSH root login restrictions and security compliance
- **Certificate Management**: Self-signed certificates used for demonstration - consider certificate authority integration for production
- **Credential Patterns**: 
  - Hardcoded credentials in deployment scripts (usernames, passwords, email addresses)
  - No encrypted secrets management detected
  - SSL private keys generated locally without external key management

### Technical Challenges

- **Minimal Migration Required**: Repository is already Ansible-based with Chef InSpec for compliance testing
- **Script Modernization**: Bash deployment scripts could be converted to Ansible playbooks for consistency
- **Credential Security**: Hardcoded credentials in shell scripts need to be externalized to Ansible Vault or environment variables
- **Test Integration**: Existing Test Kitchen + InSpec integration provides good testing framework that should be preserved

### Migration Order

1. **chef-and-ansible** (already complete - no migration needed)
2. **setup-automate scripts** (convert to Ansible playbooks for consistency)
3. **Test framework** (maintain existing InSpec integration)

### Assumptions

- This is an examples/demonstration repository rather than production infrastructure code
- The primary goal is showcasing Chef InSpec integration with Ansible rather than managing production workloads
- Current Ansible playbooks are functional and follow best practices
- Test Kitchen integration with InSpec provides adequate compliance verification
- Bash deployment scripts are used for initial Chef infrastructure setup rather than ongoing configuration management
- Target environments have internet access for package downloads and Chef Automate installation
- The repository serves educational/demonstration purposes and may not require full production-grade migration