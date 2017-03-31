import json
import re
import spineapi
import urllib2
import utopia.document
import utopia.citation
import utopialib

class EXCITEAnnotator(utopia.document.Annotator):
    '''Annotate with EXCITE related documents'''

    id_re = re.compile(r'(\d{4}\.\d+)(?:v\d+)?')

    def on_ready_event(self, document):
        arxiv_id = utopialib.utils.metadata(document, 'identifiers[arxiv]')
        if arxiv_id is not None:
            # Split up to get the base ID
            arxiv_id = id_re.match(arxiv_id).group(1)
            url = 'http://excite-compute.west.uni-koblenz.de:5555/citations/{0}'.format(arxiv_id)
            data = json.load(urllib2.urlopen(url, timeout=10))

            html = ''
            for cit in data:
                source = cit['meta_id_source']
                html += '''
                    <div class="box">{0}</div>
                '''.format(utopia.citation.render({'identifiers':{'arxiv': source}}, process=True, links=True))

            if len(html) > 0:

                html = '<p>Articles that cite this article:</p>' + html

                ann = spineapi.Annotation()
                ann['concept'] = 'Collated'
                ann['property:html'] = html
                ann['property:name'] = 'EXCITE'
                ann['property:description'] = 'Citation information from EXCITE'
                # We need to give this annotation a source icon and a source description to make it more self explanatory
                ann['property:sourceIcon'] = None
                ann['property:sourceDescription'] = '<div>What is EXCITE?</div>'
                document.addAnnotation(ann)
