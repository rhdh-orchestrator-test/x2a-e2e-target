# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and tools rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration for compliance automation, plus Chef server deployment scripts. The migration scope is minimal as most content is already Ansible-based or consists of deployment utilities.

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates, virtual host setup, and SSL protocol hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL/TLS security hardening

**poodle-ssl-fix**:
- Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 only (POODLE vulnerability mitigation)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration updates, protocol restriction, service restart handling

**chef-automate-deployment**:
- Description: Bash script for automated deployment of Chef Automate and Chef Infra Server with user and organization provisioning
- Path: setup-automate/deploy-automate.sh
- Technology: Bash scripting
- Key Features: Hostname configuration, kernel parameter tuning, Chef Automate CLI deployment, user/org creation

**chef-server-deployment**:
- Description: Bash script for standalone Chef Infra Server deployment without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash scripting
- Key Features: Chef server installation, user management, organization setup, certificate generation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: Chef InSpec security control for SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with RHEL compatibility indicated in InSpec tests
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified, designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Already integrated with Ansible for compliance testing - no migration needed
- **Apache 2.4.41**: Specific version pinned in playbook - verify availability in target environment
- **OpenSSL/PyOpenSSL**: Standard SSL certificate management - compatible with Ansible crypto modules
- **Test Kitchen**: Testing framework - can be replaced with molecule for Ansible-native testing

### Security Considerations
- **SSL/TLS Configuration**: Existing playbooks implement proper SSL hardening (TLS 1.2 enforcement, SSLv3 disabled)
- **Certificate Management**: Self-signed certificates used for demo purposes - production deployment requires proper CA-signed certificates
- **SSH Hardening**: InSpec tests verify SSH root login restrictions per STIG requirements
- **Credential Management**: Chef server deployment scripts contain hardcoded credentials that should be externalized to Ansible Vault:
  - Username: 'jtonello'
  - Password: 'password' (hardcoded)
  - Email addresses and organization names
  - Certificate file paths and names

### Technical Challenges
- **Testing Framework Migration**: Replace Test Kitchen with Molecule for Ansible-native testing workflow
- **InSpec Integration**: Maintain Chef InSpec compliance testing capabilities within Ansible ecosystem
- **Deployment Script Conversion**: Convert Bash deployment scripts to Ansible playbooks for better idempotency and error handling
- **Certificate Management**: Implement proper certificate lifecycle management for production environments

### Migration Order
1. **Testing Infrastructure** (low risk, high value): Convert Test Kitchen configuration to Molecule
2. **Deployment Automation** (moderate complexity): Convert Bash scripts to Ansible playbooks with proper variable management
3. **Compliance Integration** (high complexity): Ensure InSpec tests remain functional with migrated infrastructure

### Assumptions
- The repository serves as a demonstration/example collection rather than production infrastructure code
- Existing Ansible playbooks are already following best practices and require minimal modification
- Chef InSpec will continue to be used for compliance testing alongside Ansible
- Target environments support the specific Apache version (2.4.41) currently pinned in the playbooks
- Production deployments will replace hardcoded credentials with proper secret management
- The mixed Chef/Ansible approach is intentional for demonstrating integration capabilities rather than indicating incomplete migration