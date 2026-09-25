# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and deployment scripts rather than traditional Chef cookbooks. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, Chef server deployment scripts, and compliance testing examples. Since the repository already contains Ansible playbooks, this represents a documentation and consolidation effort rather than a traditional cookbook migration.

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates, virtual host setup, and SSL protocol hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL/TLS security hardening

**poodle-ssl-fix**:
- Description: Ansible playbook for SSL protocol hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration updates, protocol restriction, service restart handling

**chef-automate-deployment**:
- Description: Bash script for automated deployment of Chef Automate and Chef Infra Server with user and organization provisioning
- Path: setup-automate/deploy-automate.sh
- Technology: Bash scripting
- Key Features: Hostname configuration, system tuning, Chef Automate CLI installation, user/org creation

**chef-server-deployment**:
- Description: Bash script for standalone Chef Infra Server deployment without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash scripting
- Key Features: Chef server installation, user management, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG control)
- `index.html`: Static HTML test content for web server validation
- `README.md` files: Documentation for Chef InSpec and Ansible integration examples

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with RHEL compatibility for SSH security controls
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - examples are platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **apache2 (2.4.41-4ubuntu3.10)**: Already using Ansible apt module - no migration needed
- **openssl**: Already using Ansible openssl_* modules - no migration needed
- **python3-openssl**: Already using Ansible crypto modules - no migration needed
- **chef-automate-cli**: Bash deployment scripts need conversion to Ansible for consistency

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks properly implement SSL hardening by disabling SSLv3 and enforcing TLS 1.2
- **Certificate Management**: Self-signed certificates are generated using Ansible openssl modules - production environments should integrate with proper CA or certificate management systems
- **SSH Hardening**: InSpec profiles validate SSH root login restrictions per STIG requirements
- **Credential Management**: Bash deployment scripts contain hardcoded credentials (username, password, email) that should be externalized to Ansible Vault or environment variables

### Technical Challenges

- **Mixed Technology Stack**: Repository combines Ansible playbooks, Bash scripts, and InSpec tests - standardization needed
- **Hardcoded Credentials**: Chef server deployment scripts contain embedded credentials requiring vault integration
- **Test Integration**: Current Test Kitchen + InSpec workflow needs adaptation for pure Ansible testing
- **Documentation Consolidation**: Multiple README files and example formats need standardization

### Migration Order

1. **Chef Server Deployment Scripts** (moderate complexity) - Convert Bash scripts to Ansible playbooks with proper credential management
2. **Test Framework Standardization** (low complexity) - Migrate from Test Kitchen to molecule or ansible-test
3. **Documentation Consolidation** (low complexity) - Standardize examples and documentation format

### Assumptions

- The repository serves as an example/demo collection rather than production infrastructure code
- Current Ansible playbooks are already functional and don't require migration, only potential enhancement
- InSpec compliance testing framework will be retained alongside Ansible for continuous compliance validation
- Chef server deployment automation is still required and should be converted to Ansible for consistency
- Target environments support both Ubuntu and RHEL/CentOS for cross-platform compatibility
- SSL certificate management in production will use proper CA integration rather than self-signed certificates
- The mixed Chef/Ansible approach is intentional for demonstrating integration patterns rather than indicating incomplete migration