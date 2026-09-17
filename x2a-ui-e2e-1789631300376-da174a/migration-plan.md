# MIGRATION FROM MIXED ANSIBLE/CHEF INSPEC TO ANSIBLE

This repository is a demonstration/example repository that showcases using Chef InSpec alongside Ansible for compliance automation. It contains existing Ansible playbooks with Chef InSpec verification tests, rather than traditional Chef cookbooks requiring migration. The primary migration need is to replace Chef InSpec tests with native Ansible testing approaches and consolidate the Chef server deployment scripts into Ansible automation.

## Module Migration Plan

This repository contains mixed technologies that need consolidation rather than traditional migration:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host deployment for a simple "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, directory structure creation, service management

**ssl-security-hardening**:
- Description: SSL/TLS security hardening for Apache to disable vulnerable protocols (POODLE fix) and enforce TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: SSL protocol configuration, Apache module management, service restart handling

**chef-server-deployment**:
- Description: Automated Chef Automate and Chef Infra Server deployment with user and organization provisioning
- Path: setup-automate/deploy-automate.sh
- Technology: Bash scripting
- Key Features: Chef Automate installation, Chef server setup, user creation, organization management, system tuning

**chef-infra-deployment**:
- Description: Standalone Chef Infra Server deployment without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash scripting
- Key Features: Chef server installation, user provisioning, organization setup, hostname configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions
- `index.html`: Static HTML test content for web server verification
- `README.md`: Documentation explaining the Chef InSpec and Ansible integration approach

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with RHEL compatibility noted in InSpec tests
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible native testing modules (uri, assert, service_facts)
- **Test Kitchen**: Replace with molecule for Ansible playbook testing
- **Chef Automate/Server**: Migrate deployment scripts to Ansible playbooks with proper idempotency

### Security Considerations
- **SSL/TLS Configuration**: Current playbooks already implement proper SSL hardening practices
- **Certificate Management**: Self-signed certificates are used for testing - production migration should integrate with proper CA or Let's Encrypt
- **SSH Security**: InSpec tests verify SSH hardening - migrate these checks to Ansible assert tasks
- **Credential Management**: Chef server deployment scripts contain hardcoded credentials that need to be externalized to Ansible Vault
- **Service Account Security**: Chef server user creation uses default passwords that should be randomized and vaulted

### Technical Challenges
- **Test Framework Migration**: Converting Chef InSpec tests to Ansible native verification requires rewriting test logic using uri, command, and assert modules
- **Chef Server Dependencies**: The deployment scripts assume specific Chef product versions and may need updates for current releases
- **Idempotency**: Bash deployment scripts lack idempotency - Ansible conversion must handle existing installations gracefully
- **System Requirements**: Chef Automate has specific memory and disk requirements that need to be verified before deployment

### Migration Order
1. **apache-https-website** and **ssl-security-hardening** (already Ansible - focus on test migration)
2. **chef-infra-deployment** (simpler, standalone Chef server)
3. **chef-server-deployment** (more complex with Automate components)

### Assumptions
- The repository serves as a demonstration/training resource rather than production infrastructure
- Chef InSpec will be completely replaced with Ansible native testing rather than maintained alongside
- Chef server deployment is intended for lab/development environments based on the hardcoded credentials and simple configuration
- The target audience understands both Chef and Ansible ecosystems (this is a comparison/integration example)
- SSL certificates are acceptable as self-signed for demonstration purposes
- Ubuntu 20.04 package versions are acceptable or will be updated to current stable releases
- The existing Ansible playbooks follow acceptable practices and don't require significant refactoring beyond test integration