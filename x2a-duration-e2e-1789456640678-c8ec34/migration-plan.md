# MIGRATION FROM MIXED ANSIBLE/CHEF INSPEC TO ANSIBLE

This repository is a demonstration/example repository that showcases using Chef InSpec alongside Ansible for compliance automation. It contains existing Ansible playbooks with Chef InSpec verification tests, plus Chef server deployment scripts. The migration scope is minimal as the core automation is already in Ansible format - the primary task is to replace Chef InSpec tests with native Ansible testing approaches and migrate deployment scripts to Ansible playbooks.

**Migration Complexity**: Low to Medium
**Estimated Timeline**: 1-2 weeks
**Primary Challenge**: Converting Chef InSpec compliance tests to Ansible-native testing

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**poodle-ssl-fix**:
- Description: SSL security hardening playbook that disables SSLv3 and enforces TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, security compliance enforcement

**chef-automate-deployment**:
- Description: Bash script for deploying Chef Automate and Chef Infra Server with user and organization setup
- Path: setup-automate/deploy-automate.sh
- Technology: Bash Shell Script
- Key Features: Hostname configuration, system tuning, Chef Automate CLI deployment, user/org creation

**chef-server-deployment**:
- Description: Bash script for deploying standalone Chef Infra Server without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash Shell Script
- Key Features: Hostname configuration, system tuning, Chef server deployment, user/org provisioning

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `index.html`: Static HTML test page for web server verification
- `README.md`: Documentation explaining the Chef InSpec and Ansible integration approach

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible molecule, testinfra, or native Ansible assert modules
- **Test Kitchen**: Replace with Ansible molecule for testing framework
- **Chef Automate CLI**: Convert deployment scripts to Ansible playbooks using package management and service modules
- **Vagrant**: Retain for local testing or migrate to container-based testing

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks properly implement SSL hardening (TLS 1.2 enforcement, SSLv3 disabling)
- **Certificate Management**: Self-signed certificates are generated securely using Ansible openssl modules
- **SSH Security**: InSpec tests verify SSH root login is disabled - migrate these compliance checks to Ansible
- **Hardcoded Credentials**: Chef server deployment scripts contain plaintext passwords that should be moved to Ansible Vault
- **File Permissions**: Proper file permissions (0640, 0644, 0755) are already implemented in Ansible playbooks

### Technical Challenges

- **InSpec Test Migration**: Converting Chef InSpec compliance tests to Ansible-native testing approaches
  - Current tests verify port listening, HTTP responses, SSL protocol support, SSH configuration
  - Mitigation: Use Ansible uri module, assert module, and custom fact gathering for compliance verification

- **Chef Server Deployment**: Converting bash deployment scripts to idempotent Ansible playbooks
  - Scripts perform system tuning, package installation, and service configuration
  - Mitigation: Use Ansible sysctl, get_url, command, and user modules with proper error handling

- **Test Framework Transition**: Moving from Test Kitchen + InSpec to Ansible Molecule
  - Current setup uses Vagrant provisioning with InSpec verification
  - Mitigation: Implement Ansible Molecule with testinfra or native Ansible testing

### Migration Order

1. **InSpec Test Conversion** (low risk, high value)
   - Convert website_https_verify.rb and ssh_profile.rb to Ansible test tasks
   - Implement using uri, assert, and service modules

2. **Chef Server Deployment Scripts** (moderate complexity)
   - Convert deploy-automate.sh and deploy-chef-server.sh to Ansible playbooks
   - Implement proper secret management with Ansible Vault

3. **Test Framework Migration** (moderate complexity)
   - Replace Test Kitchen configuration with Ansible Molecule
   - Update CI/CD pipelines if present

### Assumptions

- The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already production-ready and require no migration
- The target environment will continue to use Ubuntu 20.04 or can be updated to a newer LTS version
- Chef InSpec compliance requirements can be satisfied using native Ansible testing capabilities
- The Chef server deployment is for development/testing purposes and not production infrastructure
- No existing Chef cookbooks or recipes need to be migrated (this is a demonstration repository)
- Test Kitchen and Vagrant are acceptable for local development testing or can be replaced with container-based alternatives
- The hardcoded credentials in deployment scripts are for demonstration purposes only