# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance testing examples alongside Ansible playbooks, representing a hybrid infrastructure-as-code approach. The migration scope is minimal as the repository already contains Ansible playbooks with Chef InSpec used for compliance verification. The primary focus is on consolidating the testing framework to use Ansible's native testing capabilities while preserving the compliance automation workflows.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (existing Ansible implementation reduces migration complexity)

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec compliance tests that need consolidation into a pure Ansible approach:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **website-https-deployment**:
    - Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL module activation, directory structure creation

- **poodle-vulnerability-fix**:
    - Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handlers

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Static HTML content for web server testing
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible's native testing modules (uri, assert, service, etc.) or molecule with testinfra
- **Test Kitchen**: Migrate to Molecule for Ansible playbook testing and verification
- **Chef Automate/Server**: Evaluate need for Chef infrastructure components in pure Ansible environment

### Security Considerations
- **SSL/TLS Configuration**: Current playbooks implement proper SSL hardening practices
  - Self-signed certificate generation using OpenSSL modules
  - POODLE vulnerability mitigation through protocol restrictions
  - Proper file permissions on certificate files (0640)
- **SSH Hardening**: InSpec profile enforces SSH root login restrictions (STIG compliance)
- **Vault/secrets management**: 
  - No encrypted secrets detected in current implementation
  - Hardcoded variables in playbooks should be moved to Ansible Vault
  - SSL certificate generation uses dynamic key creation (secure)
  - No credential patterns found requiring immediate attention

### Technical Challenges
- **InSpec to Ansible Testing Migration**: Converting Ruby-based InSpec tests to Ansible native testing requires:
  - Rewriting port and service checks using Ansible's uri and service modules
  - Converting SSL protocol verification to use openssl command module or custom facts
  - Adapting STIG compliance checks to Ansible assert statements
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires:
  - Restructuring test scenarios and verification steps
  - Adapting Vagrant driver configuration to Molecule format
  - Converting InSpec verifier to testinfra or Ansible native testing

### Migration Order
1. **InSpec Test Conversion** (Priority 1 - low risk, high value)
   - Convert website_https_verify.rb to Ansible testing tasks
   - Migrate SSH compliance profile to Ansible hardening role
2. **Test Framework Migration** (Priority 2 - moderate complexity)
   - Replace Test Kitchen with Molecule configuration
   - Adapt existing playbooks to Molecule test scenarios
3. **Infrastructure Cleanup** (Priority 3 - low complexity)
   - Evaluate need for Chef Automate deployment scripts
   - Document or remove Chef-specific infrastructure components

### Assumptions
- The repository represents a demonstration/example environment rather than production infrastructure
- Current Ansible playbooks are functional and follow best practices
- InSpec compliance requirements can be adequately addressed using Ansible native testing
- Test Kitchen usage is primarily for development/validation rather than production testing
- Chef Automate/Server deployment scripts may be retained for hybrid environments or removed if pure Ansible approach is desired
- Ubuntu 20.04 target platform will remain consistent post-migration
- Self-signed certificates are acceptable for the target environment (development/testing)
- No external Chef cookbook dependencies exist that require migration
- Vagrant-based testing environment is suitable for continued use with Molecule