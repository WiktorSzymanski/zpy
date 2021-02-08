"""
    Generic CSV dataset format.
"""
import logging
from pathlib import Path
from typing import List, Union, Callable

import gin

import zpy
from zpy.output import Output
from zpy.saver_image import ImageSaver

log = logging.getLogger(__name__)


class CSVParseError(Exception):
    """ Invalid CSV Annotation found when parsing data contents. """
    pass


@gin.configurable
class OutputCSV(Output):
    """Holds the logic for outputting CSV annotations to file."""

    ANNOTATION_FILENAME = Path('annotations.csv')

    @gin.configurable
    def output_annotations(self,
                           annotation_dict_to_csv_row_func : Callable,
                           annotation_path : Union[str, Path] = None,
                           header : List[str] = None,
                           ):
        """ Ouput Generic CSV annotations. """
        csv_data = []
        if header is not None:
            csv_data.append(header)
        for annotation in self.saver.annotations:
                row = annotation_dict_to_csv_row_func(annotation)
                if row is not None:
                    csv_data.append(row)
        # Get the correct annotation path
        if annotation_path is not None:
            annotation_path = annotation_path
        elif self.saver.annotation_path is None:
            annotation_path = self.saver.output_dir / self.ANNOTATION_FILENAME
        else:
            annotation_path = self.saver.annotation_path
        # Write out annotations to file
        zpy.files.write_csv(annotation_path, csv_data)
        # Verify annotations
        parse_csv_annotations(annotation_path)


@gin.configurable
def parse_csv_annotations(
    annotation_file: Union[str, Path],
) -> None:
    """ Parse CSV annotations """
    log.info(f'Verifying CSV annotations at {annotation_file}...')
    csv_data = zpy.files.read_csv(annotation_file)
    # Make sure all the rows are the same length
    csv_data_iterable = iter(csv_data)
    length = len(next(csv_data_iterable))
    if not all(len(l) == length for l in csv_data_iterable):
        raise CSVParseError(f'Not all rows in the CSV have same length {length}')
