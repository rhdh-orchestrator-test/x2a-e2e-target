# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains educational examples demonstrating Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec used for compliance testing. Migration complexity is minimal as the core automation is already in Ansible format.

## Module Migration Plan

This repository contains demonstration content that combines Ansible playbooks with Chef InSpec compliance testing:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, directory structure creation

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to disable SSLv3 and enforce TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache SSL protocol configuration, regex-based configuration file modification

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification in Vagrant/Ubuntu 20.04 environment
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS service availability, SSL protocol configuration, and web content delivery
- `tests/ssh_profile.rb`: InSpec security control testing SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test content for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (as specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with native Ansible testing modules (ansible.builtin.uri, ansible.builtin.service_facts, community.crypto.openssl_certificate_info)
- **Test Kitchen**: Replace with molecule for Ansible playbook testing
- **Vagrant**: Can be retained or replaced with container-based testing

### Security Considerations
- SSL/TLS configuration management: Current playbooks handle certificate generation and SSL hardening appropriately
- SSH security controls: InSpec tests verify SSH root login restrictions - migrate to Ansible assert tasks
- Self-signed certificates: Production environments should use proper CA-signed certificates or Let's Encrypt integration
- Hardcoded credentials: The setup scripts contain example credentials that should be externalized to Ansible Vault

### Technical Challenges
- **InSpec Test Migration**: Converting Ruby-based InSpec tests to Ansible native testing requires rewriting test logic using Ansible modules
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and verification methods
- **Compliance Framework**: Maintaining STIG compliance verification without InSpec requires implementing equivalent checks in Ansible

### Migration Order
1. **Website HTTPS Deployment** (low risk, already Ansible-native)
2. **POODLE Fix Playbook** (minimal changes needed)
3. **Test Infrastructure Migration** (moderate complexity, requires tooling changes)

### Assumptions
- The repository serves as educational/demonstration content rather than production infrastructure code
- InSpec compliance testing is a requirement that needs equivalent Ansible-native implementation
- Test Kitchen integration is used for development workflow and needs equivalent Molecule setup
- The Chef Automate deployment scripts are for demonstration purposes and may not require migration if used only for InSpec testing infrastructure
- Ubuntu 20.04 target platform assumption based on Test Kitchen configuration may need validation for production environments
- Self-signed certificate approach is acceptable for demonstration but production deployment would require proper certificate management strategy