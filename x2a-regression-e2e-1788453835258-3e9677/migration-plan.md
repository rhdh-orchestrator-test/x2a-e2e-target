# MIGRATION FROM CHEF INSPEC + ANSIBLE TO PURE ANSIBLE

This repository contains a hybrid Chef InSpec and Ansible demonstration setup that showcases compliance automation patterns. The migration involves consolidating the existing Ansible playbooks and replacing Chef InSpec tests with native Ansible testing approaches. The scope is limited with 2 Ansible playbooks and 2 InSpec test profiles, making this a low-complexity migration with an estimated timeline of 1-2 weeks.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and Ansible playbooks that need consolidation into a pure Ansible approach:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server with HTTPS configuration, self-signed SSL certificates, and virtual host setup for a Hello World website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: SSL certificate generation via OpenSSL modules, Apache virtual host configuration, document root setup, security hardening

**ssl-poodle-fix**:
- Description: Apache SSL configuration hardening to disable vulnerable SSL protocols and enforce TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: SSL protocol restriction, Apache configuration modification, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Static HTML test file for web server validation
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH root login security verification
- `tests/website_https_verify.rb`: InSpec test profile for HTTPS functionality and SSL protocol validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible native testing modules (uri, assert, service_facts)
- **Test Kitchen**: Replace with molecule for Ansible testing framework
- **Chef Automate/Server**: Remove deployment scripts as they're not needed for pure Ansible approach

### Security Considerations

- **SSL/TLS Configuration**: The existing playbooks already implement proper SSL hardening by disabling SSLv3 and enforcing TLS 1.2. Migration should preserve these security controls.
- **SSH Hardening**: InSpec test verifies PermitRootLogin is disabled. This should be converted to an Ansible task that enforces the configuration rather than just testing it.
- **Certificate Management**: Self-signed certificates are generated using Ansible's openssl modules. Consider migrating to ansible-vault for private key protection.
- **Vault/secrets management**: 
  - No encrypted data bags or Chef Vault usage detected
  - No hardcoded credentials found in playbooks
  - SSL private keys generated at runtime - consider vault encryption for production use
  - 0 credential patterns detected requiring immediate attention

### Technical Challenges

- **Test Framework Migration**: Converting InSpec compliance tests to Ansible native assertions requires restructuring test logic from Ruby DSL to YAML-based Ansible tasks
- **Continuous Compliance**: The current approach uses InSpec for ongoing compliance verification. Migration needs to implement equivalent continuous compliance checking using Ansible facts and assertions
- **Integration Testing**: Test Kitchen provides integrated testing workflow. Molecule migration requires reconfiguring the entire test pipeline and CI/CD integration

### Migration Order

1. **apache-https-website** (Priority 1): Low risk foundational web server setup with well-defined Ansible tasks
2. **ssl-poodle-fix** (Priority 2): Security hardening module that depends on apache-https-website base configuration
3. **Test Framework Migration** (Priority 3): Convert InSpec tests to Ansible native testing after core functionality is validated

### Assumptions

- The target environment will continue using Ubuntu 20.04 LTS as specified in the existing kitchen.yml configuration
- Test Kitchen will be replaced with Molecule as the preferred Ansible testing framework
- Chef Automate and Chef Infra Server deployment scripts will be removed as they're not relevant to pure Ansible infrastructure
- The existing Apache 2.4.41 version pinning in the playbook indicates a specific security requirement that should be maintained
- Self-signed certificates are acceptable for the target environment, though production deployments may require CA-signed certificates
- The SSH hardening requirements (PermitRootLogin disabled) represent organizational security policies that must be enforced, not just tested
- Vagrant remains the preferred local development virtualization platform
- The Hello World website represents a template for production web application deployment patterns