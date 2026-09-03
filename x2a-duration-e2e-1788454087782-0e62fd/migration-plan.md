# MIGRATION FROM MIXED CHEF/ANSIBLE TO ANSIBLE

This repository is a demonstration/example project showing Chef InSpec integration with Ansible for compliance automation. The migration scope is minimal as the primary automation is already implemented in Ansible playbooks. The main migration task involves consolidating the Chef InSpec testing framework with native Ansible testing approaches and removing Chef infrastructure dependencies.

**Migration Complexity**: Low  
**Estimated Timeline**: 1-2 weeks  
**Primary Focus**: Testing framework migration and infrastructure cleanup

## Module Migration Plan

This repository contains demonstration Ansible playbooks with Chef InSpec testing integration that need consolidation:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **website-https-deployment**:
    - Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

- **poodle-ssl-fix**:
    - Description: SSL security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2 in Apache configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: SSL protocol replacement, Apache and SSH service restart handlers, POODLE vulnerability mitigation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier - needs migration to molecule or native Ansible testing
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, port 443 listening, SSL protocol validation - needs conversion to Ansible testing modules
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login disabled (STIG control) - needs conversion to Ansible assert tasks
- `chef-and-ansible/index.html`: Static HTML test file for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script - can be removed after migration
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - can be removed after migration

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible's built-in testing modules (assert, uri, wait_for) and ansible-lint for compliance validation
- **Test Kitchen**: Migrate to Molecule for Ansible role testing and validation
- **Chef Automate/Server**: Remove infrastructure deployment scripts as they're no longer needed

### Security Considerations
- **SSL/TLS Configuration**: Current playbooks already implement proper SSL hardening (TLS 1.2 enforcement, SSL3 disabled)
- **Certificate Management**: Self-signed certificate generation is properly implemented using ansible.builtin.openssl modules
- **SSH Hardening**: InSpec test validates SSH root login disabled - convert to Ansible assert task for continuous validation
- **Vault/secrets management**: 
  - No encrypted data bags or Chef Vault usage detected
  - Hardcoded credentials found in setup scripts (userpassword='password') - should be moved to Ansible Vault
  - SSL certificate paths are properly managed through variables
  - No environment variable secrets detected
  - Total credentials detected: 2 (setup scripts contain hardcoded admin credentials)

### Technical Challenges
- **Testing Framework Migration**: Converting InSpec Ruby-based tests to Ansible native testing requires rewriting test logic in YAML format
- **Compliance Validation**: InSpec provides detailed compliance reporting - need to implement equivalent reporting with Ansible facts and custom modules
- **Test Kitchen Integration**: Current CI/CD pipeline may depend on Kitchen workflow - requires migration to Molecule or GitHub Actions with Ansible

### Migration Order
1. **Testing Framework Conversion** (Priority 1 - low risk, high value)
   - Convert InSpec tests to Ansible assert tasks
   - Implement uri module tests for HTTPS validation
   - Add service and port validation tasks
2. **Infrastructure Cleanup** (Priority 2 - low complexity)
   - Remove Chef Automate deployment scripts
   - Update documentation to remove Chef references
3. **CI/CD Pipeline Migration** (Priority 3 - moderate complexity)
   - Replace Test Kitchen with Molecule
   - Update testing workflows

### Assumptions
- The repository is primarily used for demonstration and training purposes rather than production infrastructure management
- Current Ansible playbooks are already following best practices and don't require significant refactoring
- The Chef InSpec tests are comprehensive and should be preserved in equivalent Ansible testing format
- Test Kitchen workflow is not critical to preserve - Molecule can provide equivalent functionality
- The hardcoded credentials in setup scripts are acceptable for demo purposes but should be noted as a security concern
- Ubuntu 20.04 target platform will remain consistent after migration
- No external Chef infrastructure dependencies exist beyond the local deployment scripts
- The SSL certificate generation approach (self-signed) is appropriate for the demo use case
- Current Apache version pinning (2.4.41-4ubuntu3.10) is intentional and should be preserved