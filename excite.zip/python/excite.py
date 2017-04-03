import json
import re
import spineapi
import urllib2
import utopia.document
import utopia.citation
import utopialib

class EXCITEAnnotator(utopia.document.Annotator):
    '''Annotate with EXCITE related documents'''

    # Splits the main part of the ID from the version suffix
    id_re = re.compile(r'(\d{4}\.\d+)(v\d+)?')

    # We hook into the system after the ArXiv ID has been found
    def on_ready_event(self, document):
        # Retrieve the ArXiv ID if present
        arxiv_id = utopialib.utils.metadata(document, 'identifiers[arxiv]')
        if arxiv_id is not None:
            # Simplify the ID and send it to EXCITE
            arxiv_id = id_re.match(arxiv_id).group(1)
            url = 'http://excite-compute.west.uni-koblenz.de:5555/citations/{0}'.format(arxiv_id)
            data = json.load(urllib2.urlopen(url, timeout=10))

            # Build some HTML to be put into the sidebar
            html = ''
            for cit in data:
                # Generate a live citation by processing the source ArXiv ID
                source = cit['meta_id_source']
                live = utopia.citation.render({'identifiers':{'arxiv': source}}, process=True, links=True)
                html += '''
                    <div class="box">{0}</div>
                '''.format(live)

            # Assuming any citations have been found...
            if len(html) > 0:
                html = '<p>Articles that cite this article:</p>' + html

                # Create a new annotation for this information
                ann = spineapi.Annotation()
                ann['concept'] = 'Collated'
                ann['property:html'] = html
                ann['property:name'] = 'EXCITE'
                ann['property:description'] = 'Citation information from EXCITE'
                ann['property:sourceIcon'] = utopia.get_plugin_data_as_url('images/logo.png', 'image/png')
                ann['property:sourceDescription'] = '<div><a href="http://www.gesis.org/forschung/drittmittelprojekte/projektuebersicht-drittmittel/excite/">EXCITE</a> aims for the automated extraction of citations from PDF documents.</div>'
                document.addAnnotation(ann)
