from setuptools import setup


setup(
    zip_safe=True,
    name='cloudify-openstack-adds-plugin',
    version='1.4',
    author='boucherv',
    author_email='valentin.boucher@orange.com',
    packages=[
        'designate_plugin',
        'neutron_plugin'
    ],
    license='LICENSE',
    description='Cloudify plugin for OpenStack Services',
    install_requires=[
        'cloudify-plugins-common>=3.3.1',
        'python-designateclient==1.5.0',
        'python-neutronclient==2.6.0',
        'keystoneauth1==1.2.0',
        'IPy==0.81'
    ]
)
