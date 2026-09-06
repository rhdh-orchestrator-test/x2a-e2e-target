# MIGRATION FROM MIXED CHEF/ANSIBLE TO ANSIBLE

This repository contains a hybrid Chef-Ansible demonstration environment that showcases Chef InSpec integration with Ansible playbooks for compliance automation. The migration scope is minimal as the core automation is already implemented in Ansible, with Chef components serving primarily as testing and infrastructure deployment tools. The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** for cleanup and standardization.

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a "Hello World" test site
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL/TLS enablement

**poodle-ssl-fix**:
- Description: SSL security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration hardening, TLS 1.2 enforcement, SSL protocol restriction

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with InSpec verification - requires migration to molecule or native Ansible testing
- `chef-and-ansible/index.html`: Static HTML test file for web server validation - can remain as-is
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script - requires replacement with Ansible-based deployment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - requires replacement with Ansible-based deployment
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality - requires migration to Ansible testing framework
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions - requires migration to Ansible testing framework

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox provider (based on Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Test Kitchen**: Replace with Ansible Molecule for testing and validation workflows
- **Chef InSpec**: Migrate compliance tests to Ansible's built-in testing capabilities or integrate with external compliance frameworks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible-based infrastructure provisioning
- **Vagrant**: Continue using Vagrant or migrate to container-based testing with Docker

### Security Considerations
- **SSL/TLS Configuration**: Current playbooks already implement proper SSL hardening practices including TLS 1.2 enforcement and SSL 3.0 disabling
- **Certificate Management**: Self-signed certificate generation is properly implemented using Ansible's openssl modules
- **SSH Security**: InSpec tests verify SSH root login restrictions - need to implement equivalent Ansible-based validation
- **Vault/secrets management**: 
  - Hardcoded credentials detected in setup scripts (usernames, passwords, email addresses)
  - SSL certificate paths and configurations are properly templated
  - No encrypted data bags or Chef Vault usage detected
  - **Credential Count**: 2 shell scripts contain 6 hardcoded credential values each (hostname, username, email, password, org names)

### Technical Challenges
- **Testing Framework Migration**: Converting InSpec compliance tests to Ansible-native testing requires rewriting test logic and assertions
- **Infrastructure Deployment**: Chef Automate deployment scripts need complete rewrite using Ansible modules for package management and service configuration
- **Compliance Integration**: Maintaining compliance automation capabilities without Chef InSpec requires selecting alternative compliance frameworks or implementing custom Ansible validation tasks
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and verification workflows

### Migration Order
1. **Infrastructure Deployment Scripts** (low risk, high value) - Replace shell scripts with Ansible playbooks for Chef server deployment
2. **Testing Framework** (moderate complexity) - Migrate from Test Kitchen to Molecule for consistent testing workflows
3. **Compliance Tests** (high complexity, dependencies) - Convert InSpec tests to Ansible-based validation or integrate with alternative compliance tools

### Assumptions
- The target environment will continue to use Ubuntu 20.04 LTS as specified in the current Test Kitchen configuration
- Vagrant-based local development workflow is acceptable and doesn't require migration to container-based testing
- The demonstration nature of this repository means some hardcoded values (like test certificates and sample content) are acceptable
- Chef InSpec functionality needs to be preserved through alternative compliance testing mechanisms
- The "Hello World" web application is sufficient for testing purposes and doesn't require enhancement
- SSL certificate management will remain self-signed for testing purposes rather than integrating with a proper CA
- The Apache web server configuration is appropriate for the target use case and doesn't require migration to alternative web servers
- Network security configurations (firewall rules, port restrictions) are handled at the infrastructure level and don't need to be included in the playbooks
- The current hardcoded credentials in deployment scripts are acceptable for demonstration purposes but should be parameterized for production use
- Integration with external monitoring, logging, or backup systems is not required for this demonstration environment