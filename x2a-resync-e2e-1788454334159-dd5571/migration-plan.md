# MIGRATION FROM CHEF ECOSYSTEM TO ANSIBLE

This repository contains Chef-related examples and demonstration materials that showcase integration between Chef InSpec and Ansible. The migration scope is limited as this is primarily a demonstration/example repository rather than production infrastructure code. The main migration effort involves consolidating the existing Ansible playbooks and replacing Chef InSpec testing with native Ansible testing approaches.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (demonstration code, no production dependencies)

## Module Migration Plan

This repository contains Chef ecosystem demonstration materials with existing Ansible playbooks that need consolidation and testing framework migration:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **website-https-demo**:
    - Description: Apache web server with HTTPS/SSL configuration demonstration using self-signed certificates, virtual host setup, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, directory permissions management

- **poodle-ssl-fix**:
    - Description: SSL security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration hardening, protocol restriction, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `chef-and-ansible/index.html`: Static HTML test file for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible native testing using `ansible.builtin.uri`, `ansible.builtin.wait_for`, and `ansible.builtin.assert` modules for compliance verification
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Vagrant Driver**: Maintain Vagrant for local testing or migrate to container-based testing with Molecule

### Security Considerations
- **SSL Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL Ansible modules - this approach is already Ansible-native and secure
- **SSH Security Compliance**: InSpec test for SSH root login restrictions needs migration to Ansible verification tasks
- **Apache Security Configuration**: SSL protocol restrictions are already implemented in Ansible - no migration needed
- **Vault/secrets management**: 
  - No encrypted data bags or Chef Vault usage detected
  - Hardcoded credentials found in setup scripts (userpassword='password') - 2 instances in setup-automate/ directory
  - SSL certificate paths are properly parameterized
  - No environment variable secrets detected

### Technical Challenges
- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible native verification requires rewriting Ruby-based compliance tests as Ansible tasks using uri, wait_for, and assert modules
- **STIG Compliance Verification**: SSH security compliance test (ssh_profile.rb) needs conversion from InSpec DSL to Ansible verification tasks
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test configuration and potentially changing the testing approach from Ruby to Python

### Migration Order
1. **Testing Framework Setup** (Priority 1): Implement Molecule testing framework to replace Test Kitchen
2. **InSpec Test Migration** (Priority 2): Convert website_https_verify.rb and ssh_profile.rb to Ansible verification tasks
3. **Documentation Update** (Priority 3): Update README files to reflect pure Ansible approach without Chef InSpec dependencies
4. **Setup Script Enhancement** (Priority 4): Optionally convert Chef server deployment scripts to Ansible playbooks for consistency

### Assumptions
- The repository is intended for demonstration and educational purposes rather than production deployment
- Ubuntu 20.04 remains the target platform (may need updating to newer LTS version)
- Local development/testing environment using Vagrant is acceptable (no cloud migration required)
- Chef InSpec functionality can be adequately replaced with Ansible native testing modules
- The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already properly structured and don't require significant refactoring
- Test Kitchen configuration suggests this is primarily used for local development and testing rather than CI/CD pipeline integration
- The Chef server deployment scripts in setup-automate/ are supporting infrastructure and may not require migration if the focus is on the Ansible playbook examples
- SSL certificate generation approach using Ansible OpenSSL modules is preferred over external certificate management tools
- Hardcoded credentials in setup scripts are acceptable for demonstration purposes but should be documented as requiring change for any real usage