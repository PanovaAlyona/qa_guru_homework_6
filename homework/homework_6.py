# A
# 1. Нормализация email адресов - приводит адреса к нижнему регистру и убирает пробелы
import json
from datetime import datetime


def normalize_addresses(email: dict) -> dict:
    """
    Возвращает новый словарь email, в котором адреса отправителя и получателя
    приведены к нижнему регистру и очищены от пробелов по краям.
    """
    email["sender"] = email["sender"].lower().replace(" ", "")
    email["recipient"] = email["recipient"].lower().replace(" ", "")
    return email


def add_short_body(email: dict) -> dict:
    """
    Возвращает email с новым ключом email["short_body"] —
    первые 10 символов тела письма + "...".
    """
    email["short_body"] = (
        email["body"][:10] + "..."
        if len(email["body"]) > 10
        else email["body"]
    )
    return email


def clean_body_text(body: str) -> str:
    """
    Заменяет табы и переводы строк на пробелы.
    """
    return body.replace("\t", " ").replace("\n", " ")


def build_sent_text(email: dict) -> str:
    """
    Формирует текст письма в формате:

    Кому: {to}, от {from}
    Тема: {subject}, дата {date}
    {clean_body}
    """
    return (
        f'Кому: {email["recipient"]}, от {email["sender"]}\nТема: {email["subject"]}, '
        f'дата {email["date"]}\n{email["clean_body"]}'
    )


def check_empty_fields(email: dict) -> tuple[bool, bool]:
    """
    Возвращает кортеж (is_subject_empty, is_body_empty).
    True, если поле пустое.
    """
    is_subject_empty = not email["subject"].strip()
    is_body_empty = not email["body"].strip()
    return is_subject_empty, is_body_empty


def mask_sender_email(login: str, domain: str) -> str:
    """
    Возвращает маску email: первые 2 символа логина + "***@" + домен.
    """
    return login[:2] + "***@" + domain


def get_correct_email(email_list: list[str]) -> list[str]:
    """
    Возвращает список корректных email.
    """
    correct_list = []
    for index in range(len(email_list)):
        email = email_list[index]
        if "@" in email and email.endswith((".com", ".ru", ".net")):
            correct_list.append(email)
    return correct_list


def create_email(sender: str, recipient: str, subject: str, body: str) -> dict:
    """
    Создает словарь email с базовыми полями:
    'sender', 'recipient', 'subject', 'body'
    """
    return {
        "sender": sender,
        "recipient": recipient,
        "subject": subject,
        "body": body,
    }


def add_send_date(email: dict) -> dict:
    """
    Возвращает email с добавленным ключом email["date"] — текущая дата в формате YYYY-MM-DD.
    """
    email["date"] = datetime.now().date()
    return email


def extract_login_domain(address: str) -> tuple[str, str]:
    """
    Возвращает логин и домен отправителя.
    Пример: "user@mail.ru" -> ("user", "mail.ru")
    """
    login, domain = address.split("@")
    return login, domain


# B
def sender_email(
    recipient_list: list[str],
    subject: str,
    message: str,
    *,
    sender="default@study.com",
) -> list[dict]:

    # Проверить, что recipient_list не пустой.
    if not recipient_list:
        return []

    # Проверить корректность email отправителя и получателей через get_correct_email().
    check_list = recipient_list + [sender]
    if not get_correct_email(check_list):
        return []

    # Проверить пустоту темы и тела письма через check_empty_fields(). Если одно из них пустое — вернуть пустой список.
    is_empty_subject, is_empty_body = check_empty_fields(
        {"subject": subject, "body": message}
    )
    if is_empty_subject or is_empty_body:
        return []

    # Исключить отправку самому себе: пройти по каждому элементу recipient_list в цикле for, если адрес совпадает с sender,
    # удалить его из списка.
    for email_in_list in recipient_list:
        if email_in_list == sender:
            del email_in_list

    # Нормализовать: subject и body → с помощью clean_body_text() recipient_list и sender → с помощью normalize_addresses()
    subject_clean = clean_body_text(subject)
    body_clean = clean_body_text(message)

    login, domain = extract_login_domain(sender)
    masked_sender = mask_sender_email(login, domain)
    finished_list_email = []

    for index in range(len(recipient_list)):
        email_dict = create_email(
            recipient=recipient_list[index],
            subject=subject_clean,
            body=message,
            sender=sender,
        )
        # Нормализовать: subject и body
        email_dict["clean_body"] = body_clean
        # Нормализовать: recipient_list и sender → с помощью normalize_addresses()
        email_dict = normalize_addresses(email_dict)
        # Добавить дату отправки с помощью add_send_date().
        email_dict = add_send_date(email_dict)
        # Замаскировать email отправителя с помощью extract_login_domain() и mask_sender_email().
        email_dict["masked_sender"] = masked_sender
        # Сохранить короткую версию в email["short_body"].
        email_dict = add_short_body(email_dict)
        # Сформировать итоговый текст письма функцией build_sent_text().
        finished_list_email.append(build_sent_text(email_dict))

    return finished_list_email


test_emails = [
    # Корректные адреса
    "user@gmail.com",
    "admin@company.ru",
    "test_123@service.net",
    "Example.User@domain.com",
    "default@study.com",
    " hello@corp.ru  ",
    "user@site.NET",
    "user@domain.coM",
    "user.name@domain.ru",
    "usergmail.com",
    "user@domain",
    "user@domain.org",
    "@mail.ru",
    "name@.com",
    "name@domain.comm",
    "",
    "   ",
]

emails = sender_email(
    get_correct_email(test_emails), "Information", "Skoro c neba upadut bubliki"
)
# Вернуть итоговый список писем.
print(
    f"Отправленные письма:\n", json.dumps(emails, indent=4, ensure_ascii=False)
)