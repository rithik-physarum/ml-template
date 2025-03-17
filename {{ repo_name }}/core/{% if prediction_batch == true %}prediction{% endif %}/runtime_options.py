"""
# -------------------------------------------------------------
# PYTHON File
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------
Dataflow Beam pipeline optional run time parameters.
"""

# [CAN EDIT] - ALL

from apache_beam.options.pipeline_options import PipelineOptions


# Pipline run time options
class RunTimeOptions(PipelineOptions):
    """RunTimeOptions class for optional run time parameters."""

    @classmethod
    def _add_argparse_args(cls, parser):
        """
        Add additional arguments to your Dataflow Beam pipeline.

        Use add_value_provider_argument for arguments to be templatable,
        use add_argument as usual for non-templatable arguments.

        Example
        -------
            parser.add_value_provider_argument(
                "--query",
                default="",
                help="query to read data.",
            )
            parser.add_value_provider_argument(
                "--output_table_id",
                default="",
                help="table to write predictions.",
            )
        """
        pass
