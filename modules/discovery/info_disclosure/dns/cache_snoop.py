import framework
# unique to module
import os
import dns
import re

class Module(framework.module):

    def __init__(self, params):
        framework.module.__init__(self, params)
        self.register_option('nameserver', '', 'yes', 'ip address of target\'s nameserver')
        self.register_option('domains', './data/av_domains.lst', 'yes', 'domain or list of domains to snoop for')
        self.info = {
                     'Name': 'DNS Cache Snooper',
                     'Author': 'thrapt (thrapt@gmail.com)',
                     'Description': 'Uses the DNS cache snooping technique to check for visited domains',
                     'Comments': [
                                  'Nameserver must be in IP form.',
                                  'Domains options: host.domain.com, <path/to/infile>',
                                  'http://304geeks.blogspot.com/2013/01/dns-scraping-for-corporate-av-detection.html'
                                 ]
                     }

    def module_run(self):
        domains = self.options['domains']['value']
        nameserver = self.options['nameserver']['value']
        
        if os.path.exists(domains):
            hosts = open(domains).read().split()
        else:
            hosts = [domains]
        
        self.output('Starting queries...')
        
        for host in hosts:
            status = 'Not found'
            # prepare our query
            query = dns.message.make_query(host, dns.rdatatype.A, dns.rdataclass.IN)
            # unset the Recurse flag 
            query.flags ^= dns.flags.RD
            try:
                # try the query
                response = dns.query.udp(query, nameserver)
            except KeyboardInterrupt:
                print ''
                return
            except dns.resolver.NXDOMAIN: status = 'Unknown'
            except dns.resolver.NoAnswer: status = 'No answer'
            except dns.exception.SyntaxError:
                self.error('Nameserver must be in IP form.')
                return
            except: status = 'Error'

            # searchs the response to find the answer
            if len(response.answer) > 0:
                status = 'Snooped!'
                self.alert('%s => %s' % (host, status))
            else:
                self.verbose('%s => %s' % (host, status))
