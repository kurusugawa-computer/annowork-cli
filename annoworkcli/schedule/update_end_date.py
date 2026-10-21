"""親ジョブとユーザー・現在の終了日で選んだ作業計画の終了日を一括更新する。"""

import argparse
import datetime
import logging
from collections.abc import Collection

import requests
from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.common import cli
from annoworkcli.schedule.list_schedule import ListSchedule
from annoworkcli.schedule.write_common import WriteResult, validate_dates

logger = logging.getLogger(__name__)


def validate_options(*, today: str, end_date: str, from_end_date: str | None, to_end_date: str | None) -> None:
    """日付の形式、今日以降であること、および絞り込み範囲を検証する。"""
    for date in [end_date, from_end_date, to_end_date]:
        if date is not None:
            validate_dates(today, date)
    if from_end_date is not None and to_end_date is not None:
        validate_dates(from_end_date, to_end_date)


class UpdateEndDate:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
        workspace_id: str,
        *,
        today: str,
        all_yes: bool = False,
    ) -> None:
        self.service = annowork_service
        self.workspace_id = workspace_id
        self.today = today
        self.all_yes = all_yes

    def main(
        self,
        *,
        parent_job_id: str,
        end_date: str,
        user_ids: Collection[str] | None = None,
        from_end_date: str | None = None,
        to_end_date: str | None = None,
        dry_run: bool = False,
    ) -> None:
        validate_options(today=self.today, end_date=end_date, from_end_date=from_end_date, to_end_date=to_end_date)
        reader = ListSchedule(self.service, self.workspace_id)
        schedules = reader.get_schedules(start_date=self.today, parent_job_ids=[parent_job_id], user_ids=user_ids)
        lower = from_end_date if from_end_date is not None else self.today
        # APIの日付検索は期間の重なり検索なので、現在の終了日の条件は取得後にも適用する。
        schedules = [
            schedule
            for schedule in schedules
            if schedule["parent_job_id"] == parent_job_id
            and schedule["end_date"] >= self.today
            and schedule["end_date"] >= lower
            and (to_end_date is None or schedule["end_date"] <= to_end_date)
        ]
        logger.info(f"{len(schedules)} 件の作業計画が対象です。 :: {parent_job_id=}, {end_date=}")
        result = WriteResult()
        if not schedules:
            logger.warning("条件に一致する作業計画がありません。")
            result.finish()
            return

        # 期間が逆転する計画があれば、正常な計画も含めて書き込み前に中止する。
        for schedule in schedules:
            try:
                validate_dates(schedule["start_date"], end_date)
            except ValueError as error:
                raise ValueError(
                    f"変更後の終了日が開始日より前です。 :: schedule_id='{schedule['schedule_id']}', "
                    f"start_date='{schedule['start_date']}', {end_date=}"
                ) from error

        members = {member["workspace_member_id"]: member["user_id"] for member in reader.workspace_members}
        for index, schedule in enumerate(schedules, 1):
            logger.info(
                f"{index} 件目: schedule_id='{schedule['schedule_id']}', "
                f"user_id='{members.get(schedule['workspace_member_id'], schedule['workspace_member_id'])}', "
                f"start_date='{schedule['start_date']}', end_date: {schedule['end_date']} → {end_date}"
            )
        changes = [schedule for schedule in schedules if schedule["end_date"] != end_date]
        result.skipped = len(schedules) - len(changes)
        if dry_run:
            logger.info(f"dry_run: {len(changes)} 件を変更予定です。更新は行いません。")
            result.skipped += len(changes)
            result.finish()
            return
        if not changes:
            result.finish()
            return
        if not self.all_yes and not cli.prompt_yesno(f"{len(changes)} 件の作業計画の終了日を {end_date} に変更しますか？"):
            result.skipped += len(changes)
            result.finish()
            return
        for index, schedule in enumerate(changes, 1):
            result.log_progress(index, len(changes))
            schedule_id = schedule["schedule_id"]
            body = {key: schedule[key] for key in ["workspace_member_id", "start_date", "type", "value"]}
            body.update(job_id=schedule["parent_job_id"], end_date=end_date, last_updated_datetime=schedule["updated_datetime"])
            try:
                # 確認前の更新日時を使い、一覧取得後の変更を上書きしない。
                self.service.api.put_schedule(self.workspace_id, schedule_id, request_body=body)
            except requests.exceptions.RequestException:
                logger.warning(
                    f"{index} 件目: 終了日の更新に失敗しました。 :: {schedule_id=}, before_end_date='{schedule['end_date']}', {end_date=}",
                    exc_info=True,
                )
                result.failed += 1
                continue
            logger.debug(f"{index} 件目: 終了日を更新しました。 :: {schedule_id=}")
            result.success += 1
        result.finish()


def main(args: argparse.Namespace) -> None:
    today = datetime.datetime.now().astimezone().date().isoformat()
    validate_options(today=today, end_date=args.end_date, from_end_date=args.from_end_date, to_end_date=args.to_end_date)
    workspace_id = cli.resolve_required_workspace_id(args)
    user_ids = cli.get_list_from_args(args.user_id)
    UpdateEndDate(cli.build_annoworkapi(args), workspace_id, today=today, all_yes=args.yes).main(
        parent_job_id=args.parent_job_id,
        end_date=args.end_date,
        user_ids=user_ids,
        from_end_date=args.from_end_date,
        to_end_date=args.to_end_date,
        dry_run=args.dry_run,
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    cli.add_workspace_id_argument_with_env_fallback(parser)
    parser.add_argument("-pj", "--parent_job_id", required=True, help="アサイン先の親ジョブID（1個）。指定したIDをそのまま使用します。")
    parser.add_argument("-u", "--user_id", nargs="+", help="対象ユーザーID。複数指定、file://による一覧ファイルの指定が可能です。")
    parser.add_argument("--from_end_date", help="対象となる現在の終了日の下限（YYYY-MM-DD、当日を含む、今日以降）")
    parser.add_argument("--to_end_date", help="対象となる現在の終了日の上限（YYYY-MM-DD、当日を含む、今日以降）")
    parser.add_argument("--end_date", required=True, help="変更後の終了日（YYYY-MM-DD、当日を含む、今日以降）")
    parser.add_argument("--dry_run", action="store_true", help="変更予定を表示して終了し、更新しません。")
    parser.add_argument("-y", "--yes", action="store_true", help="すべての確認に自動的にyesと答えます。")
    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    parser = cli.add_parser(
        subparsers,
        "update_end_date",
        "親ジョブ・ユーザー・現在の終了日で選んだ作業計画の終了日を一括変更します。",
        description="今日以降に終了する作業計画の終了日を一括変更します。絞り込み条件はすべてANDで適用し、範囲省略時は全計画を対象にします。",
    )
    parse_args(parser)
    return parser
