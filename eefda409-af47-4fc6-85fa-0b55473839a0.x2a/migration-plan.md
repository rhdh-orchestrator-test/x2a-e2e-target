# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository is a demonstration project showing Chef InSpec integration with Ansible for compliance automation, rather than a traditional Chef cookbook repository requiring migration. The content is already primarily Ansible-based with Chef InSpec used for testing and compliance verification. The migration scope is minimal, focusing on replacing Chef InSpec testing with native Ansible testing approaches.

## Module Migration Plan

This repository contains demonstration content that combines Ansible playbooks with Chef InSpec tests for compliance automation:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host deployment for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, directory structure setup, service management

**ssl-security-hardening**:
- Description: SSL/TLS security hardening for Apache to disable vulnerable protocols (POODLE vulnerability fix)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: SSL protocol configuration, Apache module management, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec tests for HTTPS functionality and SSL protocol compliance
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec compliance profile for SSH root login security controls
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server standalone deployment script
- `chef-and-ansible/index.html`: Static HTML test content

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible native testing modules (uri, assert, service_facts)
- **Test Kitchen**: Replace with molecule for Ansible testing framework
- **Chef Automate/Server**: Remove deployment scripts as they're not needed for pure Ansible environment

### Security Considerations
- **SSL/TLS Configuration**: The existing Ansible playbooks already implement proper SSL hardening
  - Self-signed certificate generation for development/testing
  - TLS 1.2 enforcement and SSL 3.0 disabling
  - Proper file permissions on certificate files (0640)
- **SSH Hardening**: InSpec profile tests for SSH root login restrictions need conversion to Ansible verification
- **Vault/secrets management**: 
  - Hardcoded credentials in deployment scripts (userpassword='password')
  - SSL certificate paths and configurations embedded in playbook variables
  - No encrypted vault usage detected in current implementation

### Technical Challenges
- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible native testing requires:
  - Replacing InSpec `describe` blocks with Ansible `assert` tasks
  - Converting port listening checks to `wait_for` or `service_facts` modules
  - Adapting SSL protocol verification to use `uri` module with SSL parameters
- **Compliance Reporting**: Loss of InSpec's compliance reporting capabilities requires implementing alternative reporting mechanisms
- **Integration Testing**: Test Kitchen integration needs replacement with molecule for end-to-end testing

### Migration Order
1. **Testing Framework Setup** (low risk, foundational)
   - Install and configure molecule for Ansible testing
   - Create basic test scenarios for existing playbooks
2. **InSpec Test Conversion** (moderate complexity)
   - Convert website_https_verify.rb to Ansible verification tasks
   - Convert ssh_profile.rb compliance checks to Ansible assertions
3. **Infrastructure Cleanup** (low risk)
   - Remove Chef-specific deployment scripts
   - Update documentation to reflect pure Ansible approach

### Assumptions
- The primary goal is to maintain the compliance automation demonstration while removing Chef dependencies
- Test Kitchen and Chef InSpec knowledge exists in the team for comparison during migration
- The target environment will continue to be Ubuntu-based for consistency with existing tests
- Self-signed certificates are acceptable for demonstration purposes (production would require proper CA-signed certificates)
- The demonstration nature of this repository means comprehensive error handling and production-grade security may not be required
- Molecule testing framework adoption is acceptable as a replacement for Test Kitchen
- The compliance requirements demonstrated by the InSpec profiles need to be maintained in the migrated solution