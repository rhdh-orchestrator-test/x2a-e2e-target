# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains demonstration code showing Chef InSpec integration with Ansible playbooks for compliance automation. The migration scope is minimal as the primary automation is already in Ansible format, with Chef InSpec used only for testing and compliance verification. The migration involves replacing InSpec tests with native Ansible testing approaches while preserving the existing Ansible automation logic.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec integration that need migration planning:

### MODULE INVENTORY

**website-https-automation**:
- Description: Apache web server configuration with SSL/TLS setup, self-signed certificate generation, and virtual host deployment for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (primary) + Chef InSpec (testing)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to disable SSLv3 and enforce TLS 1.2 only, addressing the POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (primary) + Chef InSpec (testing)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handling

**chef-infrastructure-deployment**:
- Description: Automated deployment scripts for Chef Automate and Chef Infra Server infrastructure setup
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation, hostname configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG control)
- `index.html`: Static HTML test file for web server verification
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment automation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible native testing modules (uri, assert, service_facts)
- **Test Kitchen**: Replace with molecule for Ansible testing framework
- **Chef Automate/Server**: Evaluate need for Chef infrastructure in pure Ansible environment

### Security Considerations

- **SSL/TLS Configuration**: Existing playbooks properly implement TLS 1.2 enforcement and disable vulnerable protocols
- **Certificate Management**: Self-signed certificates used for testing - consider integration with Let's Encrypt or internal CA for production
- **SSH Hardening**: InSpec test validates SSH root login restrictions - migrate compliance checks to Ansible assert tasks
- **Credential Management**: Hardcoded passwords in deployment scripts need migration to Ansible Vault
  - Chef server user passwords in deployment scripts
  - No encrypted data bags or Chef Vault usage detected
  - SSL certificate files managed through Ansible openssl modules

### Technical Challenges

- **InSpec Test Migration**: Convert Ruby-based InSpec controls to Ansible assert tasks and uri module checks
  - Port 443 listening verification
  - HTTPS response validation
  - SSL protocol compliance testing
- **Test Kitchen Replacement**: Migrate from Test Kitchen + Vagrant to Molecule + Docker/Podman for faster testing
- **Chef Infrastructure Dependencies**: Determine if Chef Automate/Server infrastructure is still needed in Ansible-only environment

### Migration Order

1. **website-https-automation** (low risk, already Ansible-native)
2. **poodle-vulnerability-fix** (low complexity, security-focused)
3. **chef-infrastructure-deployment** (evaluate necessity, may be deprecated)

### Assumptions

- The Chef InSpec tests are used solely for compliance verification and can be replaced with Ansible native testing
- The existing Ansible playbooks are production-ready and follow best practices
- Chef Automate and Chef Infra Server infrastructure may no longer be needed in a pure Ansible environment
- The Ubuntu 20.04 target platform will be maintained or upgraded to a supported version
- Test Kitchen usage indicates this is primarily a development/testing repository rather than production infrastructure
- The hardcoded credentials in deployment scripts are for demonstration purposes only
- SSL certificate management approach (self-signed) is acceptable for the target environment or will be enhanced separately