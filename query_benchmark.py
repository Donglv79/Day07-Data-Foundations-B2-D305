from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkQuery:
    id: int
    query: str
    gold_answer: str
    expected_doc_id: str
    expected_location: str
    required_snippets: tuple[str, ...]
    metadata_filter: dict[str, str] | None = None


BENCHMARK_QUERIES: list[BenchmarkQuery] = [
    BenchmarkQuery(
        id=1,
        query='Danh hiệu "Tập thể Tiên tiến" yêu cầu tối thiểu bao nhiêu phần trăm sinh viên đạt kết quả học tập và rèn luyện loại Khá trở lên?',
        gold_answer=(
            "Có 70% sinh viên đạt kết quả học tập và rèn luyện loại Khá trở lên; "
            "không có sinh viên xếp loại Yếu trở xuống."
        ),
        expected_doc_id="thi-dua-khen-thuong-uet-2023",
        expected_location="Điều 8",
        required_snippets=("70% sinh viên", "Tập thể Tiên tiến"),
    ),
    BenchmarkQuery(
        id=2,
        query='Điều kiện để sinh viên đạt danh hiệu "Sinh viên Xuất sắc" tại Trường Đại học Công nghệ là gì?',
        gold_answer=(
            "Kết quả học tập và rèn luyện trong năm học/toàn khóa đạt loại Xuất sắc "
            "và không có học phần nào có điểm dưới C+."
        ),
        expected_doc_id="thi-dua-khen-thuong-uet-2023",
        expected_location="Điều 4",
        required_snippets=("Sinh viên Xuất sắc", "điểm dưới C+"),
    ),
    BenchmarkQuery(
        id=3,
        query="Sinh viên Đại học Bách khoa Hà Nội phúc tra hoặc khiếu nại điểm học phần trong thời hạn bao lâu?",
        gold_answer=(
            "Được đề nghị phúc tra/khiếu nại điểm trong thời hạn 7 ngày kể từ khi "
            "điểm được cập nhật vào tài khoản học tập; không áp dụng với học phần "
            "thi vấn đáp hoặc đánh giá trước hội đồng."
        ),
        expected_doc_id="quy-che-dao-tao-dai-hoc-hust",
        expected_location="Điều 6.4",
        required_snippets=("7 ngày", "phúc tra", "vấn đáp"),
    ),
    BenchmarkQuery(
        id=4,
        query="Kể tên các danh hiệu thi đua, khen thưởng dành cho sinh viên tại Trường Đại học Công nghệ.",
        gold_answer=(
            "7 danh hiệu: Thủ khoa ngành học; Sinh viên Xuất sắc; Sinh viên Giỏi; "
            "Sinh viên có đóng góp cho công tác tập thể; Sinh viên bảo vệ khóa luận/đồ án "
            "tốt nghiệp Xuất sắc; Tập thể Tiên tiến; Tập thể Xuất sắc."
        ),
        expected_doc_id="thi-dua-khen-thuong-uet-2023",
        expected_location="Điều 3-9",
        required_snippets=("Thủ khoa ngành học", "Sinh viên Giỏi", "Tập thể Xuất sắc"),
    ),
    BenchmarkQuery(
        id=5,
        query="Quy định tạo điều kiện tham gia hoạt động nghiên cứu khoa học, trao đổi học thuật và công nhận tín chỉ áp dụng cho đối tượng nào?",
        gold_answer=(
            "Áp dụng cho sinh viên thuộc các CTĐT Tài năng thuộc nhóm chương trình ELITECH "
            "của ĐHBK Hà Nội."
        ),
        expected_doc_id="quy-che-dao-tao-dai-hoc-hust",
        expected_location="Điều 2.5",
        required_snippets=("Chương trình đào tạo Tài năng", "nghiên cứu chuyên sâu", "ELITECH"),
        metadata_filter={"audience": "student"},
    ),
]
