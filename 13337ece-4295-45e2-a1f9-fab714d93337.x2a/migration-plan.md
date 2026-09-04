# MIGRATION FROM CHEF INSPEC + ANSIBLE TO PURE ANSIBLE

This repository contains demonstration examples of Chef InSpec integration with Ansible playbooks for compliance automation. The migration involves consolidating the testing and configuration management into a unified Ansible approach using native Ansible testing modules and compliance frameworks. The scope is limited with 2 main Ansible playbooks and 2 InSpec test profiles, making this a low-complexity migration with an estimated timeline of 1-2 weeks.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec testing integration that need migration to pure Ansible with native testing capabilities:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for HTTPS website hosting
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation, directory structure creation

**poodle-ssl-fix**:
- Description: SSL security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache SSL configuration modification, protocol restriction to TLS 1.2, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `chef-and-ansible/index.html`: Static HTML test content for web server validation
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, port listening, and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG control)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for testing infrastructure
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (based on kitchen.yml platform specification and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant with VirtualBox (based on kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible native testing modules (uri, assert, service_facts) and external compliance frameworks like ansible-lint or molecule
- **Test Kitchen**: Replace with Molecule for Ansible testing or native ansible-test framework
- **Vagrant Driver**: Maintain for local testing or migrate to container-based testing with Docker
- **Chef Automate/Server**: Remove dependency as this is only used for demonstration purposes

### Security Considerations

- **SSL/TLS Configuration Management**: The current playbooks handle SSL certificate generation and Apache SSL configuration. Migration should maintain the same security posture:
  - Self-signed certificate generation using openssl_* modules (already Ansible native)
  - SSL protocol restrictions (TLS 1.2 enforcement)
  - Virtual host security configurations
- **SSH Security Compliance**: Current InSpec test validates SSH root login restrictions. Migration should include:
  - Native Ansible SSH configuration management
  - Built-in security validation using assert module or custom tasks
- **Credential Management**: No hardcoded credentials detected in the current playbooks. Variables are properly externalized.
- **Certificate Management**: SSL certificates are generated dynamically with proper file permissions (0640 for private keys)

### Technical Challenges

- **InSpec Test Translation**: Converting Ruby-based InSpec tests to Ansible native validation requires:
  - Translating `describe port(443)` to Ansible `wait_for` or `uri` module checks
  - Converting SSL protocol validation to custom Ansible tasks using `openssl` command module
  - Migrating STIG compliance checks to Ansible security role or custom validation tasks
- **Test Kitchen Replacement**: The current Vagrant-based testing workflow needs migration to:
  - Molecule for comprehensive Ansible testing
  - Docker containers for faster test execution
  - CI/CD pipeline integration for automated testing
- **Compliance Framework Integration**: Replacing Chef InSpec compliance capabilities with:
  - Ansible security roles from Ansible Galaxy
  - Custom compliance validation playbooks
  - Integration with external security scanning tools

### Migration Order

1. **website-https-deployment** (Priority 1): Low risk migration as the Ansible playbook is already complete and functional. Focus on replacing InSpec tests with native Ansible validation.
2. **poodle-ssl-fix** (Priority 2): Simple configuration change playbook with straightforward test migration requirements.
3. **Testing Infrastructure** (Priority 3): Migrate from Test Kitchen + InSpec to Molecule or ansible-test framework for comprehensive testing capabilities.

### Assumptions

- The target environment will remain Ubuntu-based as specified in the current kitchen.yml configuration
- Vagrant-based local testing is acceptable, or container-based testing with Docker is preferred for faster execution
- The demonstration nature of this repository means production-grade error handling and idempotency may need enhancement
- SSL certificate management will remain self-signed for testing purposes, but production deployments may require integration with proper CA or Let's Encrypt
- The Chef Automate/Server deployment scripts are for demonstration only and will not be migrated as they serve no purpose in a pure Ansible environment
- SSH security compliance requirements will be maintained but implemented through Ansible native modules rather than external InSpec testing
- The current hardcoded Apache version (2.4.41-4ubuntu3.10) may need updating to latest available version or made configurable through variables
- Test execution time requirements are flexible, allowing for migration from Vagrant to potentially faster container-based testing