# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and deployment scripts rather than traditional Chef cookbooks. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, deployment scripts for Chef infrastructure, and compliance testing examples. The migration scope is minimal as most content is already in Ansible format or consists of infrastructure deployment scripts.

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates, virtual host setup, and SSL protocol hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, security hardening for POODLE vulnerability

**poodle-ssl-fix**:
- Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 in Apache configurations
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: SSL protocol replacement, Apache configuration management, service restart handling

**chef-infrastructure-deployment**:
- Description: Bash scripts for automated deployment of Chef Automate and Chef Infra Server on cloud or on-premises VMs
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate CLI deployment, user and organization creation, hostname configuration, system tuning

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Vagrant driver and InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol verification, and port accessibility
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance testing (STIG-based controls)
- `index.html`: Static web content for demonstration purposes

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with Apache 2.4.41 package requirements
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, designed for generic cloud or on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated with Ansible via Test Kitchen - no migration needed
- **OpenSSL Python modules**: python3-openssl package dependency for certificate generation
- **Apache 2.4.41**: Specific version pinning may need adjustment for target environment
- **Chef Automate CLI**: Deployment scripts are infrastructure-specific, not application logic

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates used for demonstration - production migration should integrate with proper CA or certificate management system
- **Hardcoded Credentials**: Chef server deployment scripts contain plaintext passwords and user details that need to be externalized to Ansible Vault
- **SSH Security**: InSpec profiles enforce SSH root login restrictions - ensure Ansible playbooks maintain these security standards
- **SSL Protocol Hardening**: POODLE vulnerability mitigation is already implemented - verify TLS 1.2+ enforcement in target environment

### Technical Challenges

- **Test Kitchen Integration**: Current setup uses Test Kitchen with Ansible provisioner and InSpec verifier - migration may require adapting to pure Ansible testing frameworks like Molecule
- **Chef Infrastructure Dependencies**: Deployment scripts are specific to Chef ecosystem - if migrating away from Chef entirely, these become obsolete
- **Compliance Testing**: InSpec profiles provide STIG-based compliance verification - need to identify Ansible-native compliance testing alternatives or maintain InSpec integration

### Migration Order

1. **Infrastructure Deployment Scripts** (low complexity) - Convert Bash scripts to Ansible playbooks for Chef infrastructure deployment
2. **Compliance Testing Framework** (moderate complexity) - Evaluate InSpec vs Ansible-native testing approaches
3. **SSL Configuration Playbooks** (already complete) - No migration needed, already in Ansible format

### Assumptions

- The repository serves as a demonstration/example collection rather than production infrastructure code
- Current Ansible playbooks are functional and don't require migration, only potential enhancement
- Chef infrastructure deployment is still required in the target environment (if not, deployment scripts become obsolete)
- InSpec compliance testing framework will be retained alongside Ansible (hybrid approach)
- Target environment supports the same Ubuntu/Apache versions specified in current configurations
- SSL certificate management strategy (self-signed vs CA-issued) will be determined during implementation
- Test Kitchen integration with Ansible is acceptable for the target testing workflow
- Hardcoded credentials in deployment scripts are acceptable for demonstration purposes but will need Vault integration for production use