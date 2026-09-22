# MIGRATION FROM CHEF TO ANSIBLE

This repository is a demonstration/example repository that showcases Chef InSpec integration with Ansible rather than containing traditional Chef cookbooks for migration. The repository contains Ansible playbooks that are already written, Chef InSpec compliance tests, and Chef server deployment scripts. **No actual Chef cookbook migration is required** as the infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains Chef-related tooling and examples rather than production Chef cookbooks:

### MODULE INVENTORY

**No Chef cookbooks found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook that configures Apache web server with HTTPS/SSL support, self-signed certificates, and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4.41 installation, SSL certificate generation, virtual host setup, Hello World website deployment

- **poodle_fix**:
    - Description: Ansible playbook that hardens Apache SSL configuration by disabling vulnerable SSL protocols and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: SSL protocol hardening, POODLE vulnerability mitigation, Apache configuration updates

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant and Chef InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests verifying HTTPS functionality, SSL protocols, and web service availability
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying standalone Chef Infra Server
- `index.html`: Static web content for demonstration purposes

### Target Details

Based on the Ansible playbooks and Test Kitchen configuration:

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies found** - the repository uses:
- **Apache 2.4.41**: Already configured in Ansible playbook with specific Ubuntu package version
- **OpenSSL tools**: Already handled via python3-openssl and openssl packages in Ansible
- **Chef InSpec**: Used for compliance testing, not infrastructure provisioning - can remain as-is for testing

### Security Considerations

The existing Ansible implementations already address security best practices:
- **SSL/TLS Configuration**: Self-signed certificate generation with proper key management, SSL protocol hardening to disable vulnerable protocols (SSL3) and enforce TLS 1.2
- **SSH Hardening**: InSpec tests verify SSH root login is disabled (STIG compliance)
- **File Permissions**: Proper file and directory permissions set for certificates (0640) and web content (0644/0755)
- **Service Management**: Proper service restart handling through Ansible handlers

### Technical Challenges

**No migration challenges** - this is an example repository demonstrating Chef InSpec integration with Ansible:
- Infrastructure automation is already implemented in Ansible
- Chef InSpec tests provide compliance verification and can continue to be used
- Test Kitchen provides integration testing framework that works with Ansible

### Migration Order

**No migration required** - repository structure suggests this is for:
1. Demonstrating Chef InSpec compliance testing with Ansible playbooks
2. Providing examples for Chef-to-Ansible integration patterns
3. Setting up Chef server infrastructure for testing purposes

### Assumptions

- This repository serves as a demonstration/example rather than production infrastructure code
- The Chef InSpec tests are intended to remain as compliance verification tools alongside Ansible
- The Chef server deployment scripts are for setting up testing/development environments
- No actual Chef cookbooks exist that require migration to Ansible
- The existing Ansible playbooks represent the target state rather than source material for migration
- Test Kitchen configuration suggests this is used for local development and testing workflows
- The repository demonstrates how organizations can use Chef InSpec for compliance while using Ansible for infrastructure automation